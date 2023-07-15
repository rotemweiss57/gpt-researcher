import os

from pymongo import MongoClient
from datetime import datetime

def query2db(query, agents, report_type):
    # Connect to the MongoDB server
    usr = os.getenv('MONGO_USER')
    pwd = os.getenv('MONGO_PWD')
    client = MongoClient(f"mongodb+srv://{usr}:{pwd}@cluster0.47o7jxs.mongodb.net/?retryWrites=true&w=majority")

    # Connect to the "Tavily" database
    db = client['Tavily']

    # Get the "ResearchQueries" collection
    collection = db['ResearchQueries']

    # Create the document to be inserted
    document = {
        'query': query,
        'agent': agents,
        'report_type': report_type,
        'created': datetime.now()
    }

    # Insert the document into the collection
    collection.insert_one(document)

    # Close the connection
    client.close()


