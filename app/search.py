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

#   function for querying elasticsearch index
def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page}
    )

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


    