import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

load_dotenv()


def get_db_connection():
    uri = os.getenv("MONGO_URI")
    print(f"DEBUG: My URI is: {uri}")
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client["cs361"]
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


db = get_db_connection()


def get_collections():
    if db is not None:
        return db['travel_hub'], db['travel_dates']
    return None, None


def get_all_items():
    collection, _ = get_collections()
    if collection is not None:
        return list(collection.find())
    else:
        return []


def add_item(place, info):
    collection, _ = get_collections()
    if collection is not None:
        collection.insert_one({'place': place, 'info': info})
        print("Data added to database")


def delete_item(item_id):
    collection, _ = get_collections()
    if collection is not None:
        collection.delete_one({"_id": ObjectId(item_id)})


def delete_collection():
    collection, _ = get_collections()
    if collection is not None:
        collection.delete_many({})
        print("the list was deleted")


def get_item_by_id(item_id):
    collection, _ = get_collections()
    if collection is not None:
        return collection.find_one({"_id": ObjectId(item_id)})
    return None


def update_item(item_id, place, info):
    collection, _ = get_collections()
    if collection is not None:
        collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {"place": place, "info": info}}
        )
