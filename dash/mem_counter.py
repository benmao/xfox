"""A high performance counter without sharding.
Original Version: http://appengine-cookbook.appspot.com/recipe/high-concurrency-counters-without-sharding

Improvements:
  1) Off by one?: The deferred memcache.decr() subtracts count where count is
     the current memcache value **plus 1**.  This means that the memcache value
     will actually be decremented 1 too much.  This will result in a missed count
     if the counter is incremented between the time the memcached.decr() task is
     enqueued and when it actually runs (otherwise it isn't a problem since the
     value won't decrease below 0).
  2) memcache.decr() doesn't need to be a transactional task.  memcache.decr()
     could still "fail" (it returns None to indicate failure, but this won't
     cause the task to be retried).
  3) The increment amount can now be tweaked (the default is still 1).
  4) CounterModel is explicitly defined.
  5) Replaced db.get with Model.get_by_key_name since key is a str not db.Key.

Limitations:
  1) Like the original code, this may undercount if memcache evicts a counter
     which hasn't been persisted to the db (e.g., a spike it traffic followed by
     no traffic).  It may also undercount if memcache.incr() fails.
  2) This may double-count if a memcache.decr() fails.  But this event seems
     very unlikely.  If it does happen, it will be logged.
  3) To get the count, you must fetch it from the datastore (the memcache
     counter only has the *change* to the datastore's value).

# initialize the empty counter in the datastore
>>> time = __import__('time')
>>> key = "test"
>>> update_interval = 1  # for testing purposes, flush to datastore after 1sec

# increment the counter (this will go to the datastore)
>>> incrementCounter(key, update_interval=update_interval)

>>> memcache.get("counter_val:%s" % key) is None
True
>>> CounterModel.get_by_key_name(key).counter
1L

# increment it some more (won't go to the datastore: update_interval hasn't passed)
>>> incrementCounter(key, update_interval=update_interval)
>>> incrementCounter(key, delta=5, update_interval=update_interval)
>>> memcache.get("counter_val:%s" % key)
'6'
>>> CounterModel.get_by_key_name(key).counter
1L

# wait for the update_interval to expire
>>> time.sleep(1.0)

# this should go to the datastore
>>> incrementCounter(key, update_interval=update_interval)
>>> memcache.get("counter_val:%s" % key)
'0'
>>> CounterModel.get_by_key_name(key).counter
8L

# increment it some more (won't go to the datastore: update_interval hasn't passed)
>>> incrementCounter(key, update_interval=update_interval)
>>> memcache.get("counter_val:%s" % key)
'1'
>>> CounterModel.get_by_key_name(key).counter
8L

# simulate the memcache entry being evicted => will undercount
>>> memcache.flush_all()
True
>>> memcache.get("counter_val:%s" % key) is None
True
>>> CounterModel.get_by_key_name(key).counter
8L

# simulate memcache.decr() failing => will double count
>>> incrementCounter(key, update_interval=update_interval)  # goes to db
>>> incrementCounter(key, update_interval=update_interval)  # memcache only
>>> time.sleep(1.0)
>>> memcache.decr_real = memcache.decr
>>> memcache.decr = lambda key, delta : None
>>> incrementCounter(key, update_interval=update_interval)  # to db, but decr fails
>>> memcache.decr = memcache.decr_real

# memcache.decr() failed, but the db was updated => next update will double-count hits between this db write and prev db write
>>> memcache.get("counter_val:%s" % key)
'1'
>>> CounterModel.get_by_key_name(key).counter
11L
"""

import logging

from google.appengine.api import memcache
from google.appengine.ext import db

class CounterModel(db.Model):
    counter = db.IntegerProperty()

def incrementCounter(key, delta=1, update_interval=10):
    """Increments a memcached counter.
    Args:
      key: The key of a datastore entity that contains the counter.
      delta: Non-negative integer value (int or long) to increment key by, defaulting to 1.
      update_interval: Minimum interval between updates.
    """
    lock_key  = "counter_lock:%s" % (key,)
    count_key = "counter_val:%s" % (key,)

    if memcache.add(lock_key, None, time=update_interval):
        # Time to update the DB
        prev_count = int(memcache.get(count_key) or 0)
        new_count = prev_count + delta

        def tx():
            entity = CounterModel.get_by_key_name(key)
            if not entity:
                entity = CounterModel(key_name=key, counter=0)
            entity.counter += new_count
            entity.put()

        try:
            db.run_in_transaction(tx)
            if prev_count>0 and memcache.decr(count_key, delta=prev_count) is None:
                logging.warn("counter %s could not be decremented (will double-count): %d" % (key, prev_count))
        except Exception, e:
            # db failed to update: we'll try again later; just add delta to memcache like usual for now
            memcache.incr(count_key, delta, initial_value=0)
    else:
        # Just update memcache
        memcache.incr(count_key, delta, initial_value=0)

