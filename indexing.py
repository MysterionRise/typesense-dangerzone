import json

import typesense

# Initialize the client
client = typesense.Client(
    {
        "nodes": [
            {
                "host": "localhost",  # For Typesense server
                "port": "8108",  # The default port is 8108
                "protocol": "http",  # Use 'https' for SSL
            }
        ],
        "api_key": "abcd",
        "connection_timeout_seconds": 2,
    }
)

schema = {
    "name": "movies",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "Title", "type": "string"},
        {"name": "imdbRating", "type": "string"},
    ],
}

client.collections.create(schema)

file_path = "movies.json"

# Reading the JSON file
with open(file_path, "r") as file:
    movies = json.load(file)

# Indexing the documents
for movie in movies:
    client.collections["movies"].documents.upsert(movie)

print(client.collections["movies"].documents.export())
