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
import sys
import os
from google.appengine.ext import db
from google.appengine.datastore import entity_pb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from django.utils import simplejson

def get_protobuf_from_entity(entities):
    """Converts one or more {{{db.Model}}} instances to encoded Protocol Buffers.

    This is useful to store entities in memcache, and preferable than storing
    the entities directly as it has slightly better performance and avoids
    crashes when unpickling (when, for example, the entity class is moved to a
    different module).

    Cached protobufs can be de-serialized using [[get_entity_from_protobuf]].

    Example usage:

    <<code python>>
    from google.appengine.api import memcache
    from tipfy.ext.db import get_protobuf_from_entity

    # Inside a handler, given that a MyModel model is defined.
    entity = MyModel(key_name='foo')
    entity.put()

    # Cache the protobuf.
    memcache.set('my-cache-key', get_protobuf_from_entity(entity))
    <</code>>

    This function derives from [[http://blog.notdot.net/2009/9/Efficient-model-memcaching|Nick's Blog]].

    * Parameters:
    ** entities: A single or a list of {{{db.Model}}} instances to be serialized.

    ** Return:
    ** One or more entities serialized to Protocol Buffer (a string or a
       list).
    """
    if not entities:
        return None
    elif isinstance(entities, db.Model):
        return db.model_to_protobuf(entities).Encode()
    elif isinstance(entities, dict):
        return dict((k, db.model_to_protobuf(v).Encode()) for k, v in \
        entities.iteritems())
    else:
        return [db.model_to_protobuf(x).Encode() for x in entities]


def get_entity_from_protobuf(data):
    """Converts one or more encoded Protocol Buffers to {{{db.Model}}} instances.

    This is used to de-serialize entities previously serialized using
    [[get_protobuf_from_entity]]. After retrieving an entity protobuf
    from memcache, this converts it back to a {{{db.Model}}} instance.

    Example usage:

    <<code python>>
    from google.appengine.api import memcache
    from tipfy.ext.db import get_entity_from_protobuf

    # Get the protobuf from cache and de-serialize it.
    protobuf = memcache.get('my-cache-key')
    if protobuf:
        entity = get_entity_from_protobuf(protobuf)
    <</code>>

    This function derives from [[http://blog.notdot.net/2009/9/Efficient-model-memcaching|Nick's Blog]].

    * Parameters:
    ** data: One or more entities serialized to Protocol Buffer (a string or a
       list).

    ** Return:
    ** One or more entities de-serialized from Protocol Buffers (a
       {{{db.Model}}} inatance or a list of {{{db.Model}}} instances).
    """
    if not data:
        return None
    elif isinstance(data, str):
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    elif isinstance(data, dict):
        return dict((k, db.model_from_protobuf(entity_pb.EntityProto(v))) \
            for k, v in data.iteritems())
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]


def get_reference_key(entity, prop_name):
    """Returns a encoded key from a {{{db.ReferenceProperty}}} without fetching
    the referenced entity.

    Example usage:

    <<code python>>
    from google.appengine.ext import db
    from tipfy.ext.db import get_reference_key

    # Set a book entity with an author reference.
    class Author(db.Model):
        name = db.StringProperty()

    class Book(db.Model):
        title = db.StringProperty()
        author = db.ReferenceProperty(Author)

    author = Author(name='Stephen King')
    author.put()

    book = Book(key_name='the-shining', title='The Shining', author=author)
    book.put()

    # Now let's fetch the book and get the author key without fetching it.
    fetched_book = Book.get_by_key_name('the-shining')
    assert str(author.key()) == str(get_reference_key(fetched_book,
        'author'))
    <</code>>

    * Parameters:
    ** entity: A {{{db.Model}}} instance.
    ** prop_name: The name of the {{{db.ReferenceProperty}}} property.

    ** Return:
    ** An entity Key, as a string.
    """
    return getattr(entity.__class__, prop_name).get_value_for_datastore(entity)

def populate_entity(entity, **kwargs):
    """Sets a batch of property values in an entity. This is useful to set
    multiple properties coming from a form or set in a dictionary.

    Example usage:

    <<code python>>
    from google.appengine.ext import db
    from tipfy.ext.db import populate_entity

    class Author(db.Model):
        name = db.StringProperty(required=True)
        city = db.StringProperty()
        state = db.StringProperty()
        country = db.StringProperty()

    # Save an author entity.
    author = Author(key_name='stephen-king', name='Stephen King')
    author.put()

    # Now let's update the record.
    author = Author.get_by_key_name('stephen-king')
    populate_entity(author, city='Lovell', state='Maine', country='USA')
    author.put()
    <</code>>

    * Parameters:
    ** entity: A {{{db.Model}}} instance.
    ** kwargs: Keyword arguments for each entity property value.

    ** Return:
    ** {{{None}}}
    """
    properties = get_entity_properties(entity)
    for key, value in kwargs.iteritems():
        if key in properties:
            setattr(entity, key, value)


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

def clone_entity(e, **extra_args):
    """Clones an entity, adding or overriding constructor attributes.
    
    The cloned entity will have exactly the same property values as the original
    entity, except where overridden. By default it will have no parent entity or
    key name, unless supplied.
    
    Args:
      e: The entity to clone
      extra_args: Keyword arguments to override from the cloned entity and pass
        to the constructor.
    Returns:
      A cloned, possibly modified, copy of entity e.
    """
    klass = e.__class__
    props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
    props.update(extra_args)
    return klass(**props)
