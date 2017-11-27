if mode == 'online' and result_id != None:
    # call RAKE and extract keywords
    document_id = str(result_id)
    online_processing_rake(document_id, mongo_object)