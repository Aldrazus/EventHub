from flask import current_app
from app import db
from app.models import User, Event

from datetime import datetime, timedelta
from dateutil import tz

#   List of new/updated objects in this current session
added_objs = []
#   List of removed objects in this current session
removed_objs = []


#   Dictionary of time ranges (keys) and filter queries (values)
TIME_RANGE_FILTERS = {
    'today': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=1) },
    'week': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=7) },
    'month': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=30) },
}

#   Stores added/updated and deleted objects in global variables to be added/removed from search index.
#   To be called before commit.
def before_commit(session):
    global added_objs, removed_objs
    added_objs += list(session.new) + list(session.dirty)
    removed_objs = list(session.deleted)

#   Adds new/updated objects to search index and removes deleted objects from search index.
#   To be called after commit.
def after_commit(session):
    global added_objs, removed_objs

    for obj in added_objs:
        if isinstance(obj, (User, Event)):
            add_to_index(obj.__tablename__, obj)
    for obj in removed_objs:
        if isinstance(obj, (User, Event)):
            remove_from_index(obj.__tablename__, obj)

    added_objs, removed_objs = list(), list()
    

db.event.listen(db.session, 'before_commit', before_commit)
db.event.listen(db.session, 'after_commit', after_commit)

#   Adds searchable fields of model to search index
#   Usage of __searchable__ field to index specific fields sourced from here: 
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
def add_to_index(index, model):
    #only use if elasticsearch is enabled
    if not current_app.elasticsearch:
        return
    
    #data to be indexed
    payload = {}

    # can do -> if isinstance(model, (User)):

    #check __searchable__ field in model for list of searchable fields
    for field in model.__searchable__:
        #add this field to payload to be indexed
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

#   Removes searchable model fields from index.
def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

#   Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
#   Text Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html
#   Multi-match Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html

#   Queries search engine for user using Elasticsearch's REST API and Query DSL.
def query_user(query):
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index='user',
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}}}
    )

    #TODO: Try this solution? https://stackoverflow.com/questions/16776260/elasticsearch-multi-match-with-filter
    # search = current_app.elasticsearch.search(
    #     index=index,
    #     body={'query': {'multi_match': {
    #         'query': query, 'fields': ['*']}},
    #         'filter': {'range': {'start_time': { 'lte': start_time, 'gte': end_time }}},
    #         'from': (page - 1) * per_page, 'size': per_page}
    # )

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    print(ids, query)
    return ids, search['hits']['total']['value']

#   Queries search engine for event using Elasticsearch's REST API and Query DSL.
def query_event(query, location=None, time=None):
    if not current_app.elasticsearch:
        return [], 0
    
    if not (location is None):
        query = ' '.join([query, location])

    #https://stackoverflow.com/questions/16776260/elasticsearch-multi-match-with-filter
    query_body = {
        'query': {
            'bool': {
                'must': {
                    'multi_match': {
                        'query': query, 'fields': ['*']
                    }
                }
            }
        }
    }   

    if not (time is None):
        query_body['query']['bool']['filter'] = []
        query_body['query']['bool']['filter'].append({
            'range': {
                'start_time': TIME_RANGE_FILTERS[time]
            }
        })


    search = current_app.elasticsearch.search(
        index='event',
        body=query_body
    )

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']

#   Searches for given class using appropriate query function.
def search(cls, expression, location=None, time=None):
    ids, total = [], 0
    if cls.__tablename__ == 'event':
        ids, total = query_event(expression, location, time)
    elif cls.__tablename__ == 'user':
        ids, total = query_user(expression)
    else:
        print('invalid index')
    if total == 0:
        return cls.query.filter_by(id=0), 0

    #lists the events in order of relevance, (ID1, 1), (ID2, 2), ...
    #gets actual events from ids
    when = [(ids[i], i) for i in range(len(ids))]
    return cls.query.filter(cls.id.in_(ids)).order_by(
        db.case(when, value=cls.id)), total


    