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

client.collections["movies"].delete()
