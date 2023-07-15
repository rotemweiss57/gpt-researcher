import os
from pymongo import MongoClient
from datetime import datetime, timedelta

def query2db(query, agent, report_type, start_time):
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
        'agent': agent,
        'report_type': report_type,
        'start_time': start_time,
        'end_time': None,
        'total_time': None,
        'report_path': None,
        'status': 'started',
        'created': datetime.now()
    }

    # Insert the document into the collection
    result = collection.insert_one(document)

    # Get the _id of the inserted document
    document_id = result.inserted_id

    # Close the connection
    client.close()

    # Return the _id of the inserted document
    return document_id



def update_query(document_id, path, end_time, total_time):
    # Convert total_time to seconds
    total_time_seconds = total_time.total_seconds()

    # Connect to the MongoDB server
    usr = os.getenv('MONGO_USER')
    pwd = os.getenv('MONGO_PWD')
    client = MongoClient(f"mongodb+srv://{usr}:{pwd}@cluster0.47o7jxs.mongodb.net/?retryWrites=true&w=majority")

    # Connect to the "Tavily" database
    db = client['Tavily']

    # Get the "ResearchQueries" collection
    collection = db['ResearchQueries']

    # Create the update query
    update_query = {
        '$set': {
            'end_time': end_time,
            'total_time': total_time_seconds,
            'report_path': path,
            'status': 'finished'
        }
    }

    # Update the document in the collection
    collection.update_one({'_id': document_id}, update_query)

    # Close the connection
    client.close()
