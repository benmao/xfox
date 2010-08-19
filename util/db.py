# -*- coding: utf-8 -*-
"""
= tipfy.ext.db

db.Model utilities extension.
"""
import hashlib
import logging
import pickle
import re
import time
import unicodedata

from google.appengine.ext import db
from google.appengine.datastore import entity_pb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from django.utils import simplejson



class ModelMixin(object):
    """A base class for db.Model mixins. This allows to mix db properties
    from several base classes in a single model. For example:

    <<code python>>
    from google.appengine.ext import db

    from tipfy.ext.db import ModelMixin

    class DateMixin(ModelMixin):
        created = db.DateTimeProperty(auto_now_add=True)
        updated = db.DateTimeProperty(auto_now=True)

    class AuditMixin(ModelMixin):
        created_by = db.UserProperty()
        updated_by = db.UserProperty()

    class Account(db.Model, DateMixin, AuditMixin):
        name = db.StringProperty()

    class SupportTicket(db.Model, DateMixin, AuditMixin):
        title = db.StringProperty()

    class Item(db.Model, DateMixin):
        name = db.StringProperty()
        description = db.StringProperty()
    <</code>>

    Read more about it in the
    [[http://www.tipfy.org/wiki/cookbook/reusing-models-with-modelmixin/|tutorial]].
    """
    __metaclass__ = db.PropertiedClass

    @classmethod
    def kind(self):
        """Need to implement this because it is called by PropertiedClass
        to register the kind name in _kind_map. We just return a dummy name.
        """
        return '__model_mixin__'


# Extra db.Model property classes.
class EtagProperty(db.Property):
    """Automatically creates an ETag based on the value of another property.

    Note: the ETag is only set or updated after the entity is saved.

    Example usage:

    <<code python>>
    from google.appengine.ext import db
    from tipfy.ext.db import EtagProperty

    class StaticContent(db.Model):
        data = db.BlobProperty()
        etag = EtagProperty(data)
    <</code>>

    This class derives from [[http://github.com/Arachnid/aetycoon|aetycoon]].
    """
    def __init__(self, prop, *args, **kwargs):
        self.prop = prop
        super(EtagProperty, self).__init__(*args, **kwargs)

    def get_value_for_datastore(self, model_instance):
        v = self.prop.__get__(model_instance, type(model_instance))
        if not v:
            return None

        if isinstance(v, unicode):
            v = v.encode('utf-8')

        return hashlib.sha1(v).hexdigest()


class JsonProperty(db.Property):
    """Stores a value automatically encoding to JSON on set and decoding
    on get.

    Example usage:

    <<code python>>
    >>> class JsonModel(db.Model):
    ... data = JsonProperty()
    >>> model = PickleModel()
    >>> model.data = {"foo": "bar"}
    >>> model.data
    {'foo': 'bar'}
    >>> model.put() # doctest: +ELLIPSIS
    datastore_types.Key.from_path(u'PickleModel', ...)
    >>> model2 = PickleModel.all().get()
    >>> model2.data
    {'foo': 'bar'}
    <</code>>
    """
    data_type = db.Text

    def get_value_for_datastore(self, model_instance):
        """Encodes the value to JSON."""
        value = super(JsonProperty, self).get_value_for_datastore(
            model_instance)
        if value is not None:
            return db.Text(simplejson.dumps(value))

    def make_value_from_datastore(self, value):
        """Decodes the value from JSON."""
        if value is not None:
            return simplejson.loads(value)

    def validate(self, value):
        if value is not None and not isinstance(value, (dict, list, tuple)):
            raise db.BadValueError('Property %s must be a dict, list or '
                'tuple.' % self.name)

        return value


class PickleProperty(db.Property):
    """A property for storing complex objects in the datastore in pickled form.

    Example usage:

    <<code python>>
    >>> class PickleModel(db.Model):
    ... data = PickleProperty()
    >>> model = PickleModel()
    >>> model.data = {"foo": "bar"}
    >>> model.data
    {'foo': 'bar'}
    >>> model.put() # doctest: +ELLIPSIS
    datastore_types.Key.from_path(u'PickleModel', ...)
    >>> model2 = PickleModel.all().get()
    >>> model2.data
    {'foo': 'bar'}
    <</code>>

    This class derives from [[http://github.com/Arachnid/aetycoon|aetycoon]].
    """
    data_type = db.Blob

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        value = self.validate(value)

        if value is not None:
            return db.Blob(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))

    def make_value_from_datastore(self, value):
        if value is not None:
            return pickle.loads(str(value))


class SlugProperty(db.Property):
    """Automatically creates a slug (a lowercase string with words separated by
    dashes) based on the value of another property.

    Note: the slug is only set or updated after the entity is saved.

    Example usage:

    <<code python>>
    from google.appengine.ext import db
    from tipfy.ext.db import SlugProperty

    class BlogPost(db.Model):
        title = db.StringProperty()
        slug = SlugProperty(title)
    <</code>>

    This class derives from [[http://github.com/Arachnid/aetycoon|aetycoon]].
    """
    def __init__(self, prop, max_length=None, *args, **kwargs):
        self.prop = prop
        self.max_length = max_length
        super(SlugProperty, self).__init__(*args, **kwargs)

    def get_value_for_datastore(self, model_instance):
        v = self.prop.__get__(model_instance, type(model_instance))
        if not v:
            return self.default

        return _slugify(v, max_length=self.max_length, default=self.default)


