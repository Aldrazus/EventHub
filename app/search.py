from flask import current_app

#   function for adding searchable model fields to index
def add_to_index(index, model):
    #only use if elasticsearch is enabled
    if not current_app.elasticsearch:
        return
    
    #data to be indexed
    payload = {}

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

def query_user_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    #Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
    #Text Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html
    #Multi-match Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page}
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


#   function for querying elasticsearch index
def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    #Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
    #Text Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html
    #Multi-match Queries: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page}
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


    