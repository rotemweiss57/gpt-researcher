import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import NoCredentialsError


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



# Initialize the S3 client
s3 = boto3.client('s3')


def upload_to_s3(file_path, bucket):
    file_name = file_path.split("/")[-1]  # get the filename from the path
    try:
        # Upload the file
        s3.upload_file(
            Filename=file_path,
            Bucket=bucket,
            Key=file_name,
            ExtraArgs={
                'ACL': 'public-read',  # this will make the file publicly readable
                'ContentType': 'application/pdf'
            }
        )

        print("Upload Successful")
        return f"https://{bucket}.s3.amazonaws.com/{file_name}"

    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None

