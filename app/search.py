from flask import current_app
from app import db
from app.models import User, Event

from datetime import datetime, timedelta
from dateutil import tz

added_objs = []
removed_objs = []

#TODO: ADD BACK PAGES

#TODO: Get these time filters done!
TIME_RANGE_FILTERS = {
    'today': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=1) },
    'week': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=7) },
    'month': { 'gte': datetime.today(), 'lte': datetime.today() + timedelta(days=30) },
}


def before_commit(session):
    global added_objs, removed_objs
    added_objs += list(session.new) + list(session.dirty)
    removed_objs = list(session.deleted)

def after_commit(session):
    global added_objs, removed_objs

    for obj in added_objs:
        if isinstance(obj, (User, Event)):
            add_to_index(obj.__tablename__, obj)
    for obj in removed_objs:
        if isinstance(obj, (User, Event)):
            remove_from_index(obj.__tablename__, obj)

    added_objs, removed_objs = [], []
    

db.event.listen(db.session, 'before_commit', before_commit)
db.event.listen(db.session, 'after_commit', after_commit)

#   function for adding searchable model fields to index
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

#   function for removing searchable model fields from index
def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_user(query):
    if not current_app.elasticsearch:
        return [], 0

    #Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
    #Text Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html
    #Multi-match Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
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
    return ids, search['hits']['total']['value']

def query_event(query, location=None, time=None):
    if not current_app.elasticsearch:
        return [], 0

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

    if not (location is None) or not (time is None):
        query_body['query']['bool']['filter'] = []
        if not (location is None):
            query_body['query']['bool']['filter'].append({
                'term': {
                    'location': location
                }
            })
        if not (time is None):
            query_body['query']['bool']['filter'].append({
                'range': {
                    'start_time': TIME_RANGE_FILTERS[time]
                }
            })

    #print(query_body)

    search = current_app.elasticsearch.search(
        index='event',
        body=query_body
    )

    #print(search)

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']

#pass query data as dict maybe
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


    