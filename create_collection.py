from typesense import client

schema = {
    "name": "companies",
    "fields": [
        {"name": "company_name", "type": "string"},
        {"name": "num_employees", "type": "int32"},
        {"name": "country", "type": "string", "facet": True},
    ],
    "default_sorting_field": "num_employees",
}

client.collections.create(schema)
