
fixture = """
{'id':'project_id:dataset.table_id', 
'schema': 
{'fields': [
{'name': 'pk_obt_penetrace', 'type': 'STRING', 'description':'test'},
{'name': 'penetrace_cohort_id', 'type': 'INTEGER', 'description': 'x.'},
{'name': 'penetrace_question_id', 'type': 'INTEGER', 'description': 'not_yet_documented'},
{'name': 'weekly_data', 'type': 'RECORD', 'mode': 'REPEATED', 
'fields': [
    {'name': 'question_cohort_week_id', 'type': 'STRING', 'description': ''}, 
    {'name': 'start_of_week', 'type': 'DATE', 'description': ''}, 
    {'name': 'question_respondent_count_total', 'type': 'INTEGER', 'description': ''},
    {'name': 'question_respondent_count_4_week_total', 'type': 'INTEGER', 'description': ''},
    {'name': 'question_respondent_count_12_week_total', 'type': 'INTEGER', 'description': ''}, 
    {'name': 'answer_value_response_information', 'type': 'RECORD', 'mode': 'REPEATED', 
    'fields': [
        {'name': 'penetrace_struct_id', 'type': 'STRING', 'description': ''}, 
        {'name': 'answer_value', 'type': 'STRING','description': ''}, 
        {'name': 'answer_value_respondent_count', 'type': 'INTEGER', 'description': ''}, 
        {'name': 'answer_value_respondent_count_4_week_total', 'type': 'INTEGER', 'description': ''},
        {'name': 'answer_value_respondent_count_12_week_total', 'type': 'INTEGER', 'description': ''},
        {'name': 'respondent_ids_array', 'type': 'INTEGER', 'mode': 'REPEATED', 'description': ''}
    ]}
], 'description': ''}, 
]},
'numBytes': '84488832516', 
'numLongTermBytes': '0',
'numRows': '12574674',
'creationTime': '1744101302478',
'expirationTime': '4897701291235',
'lastModifiedTime': '1744101303558', 
'type': 'TABLE', 
'location': 'EU', 
'clustering': {'fields': ['question_category', 'question_sub_category']}, 
'numTimeTravelPhysicalBytes': '101129439608', 
'numTotalLogicalBytes': '84488832516',
'numActiveLogicalBytes': '84488832516', 
'numLongTermLogicalBytes': '0', 
'numTotalPhysicalBytes': '121364892536', 
'numActivePhysicalBytes': '121364892536', 
'numLongTermPhysicalBytes': '0', 
'numCurrentPhysicalBytes':'20235452928'
} 
"""