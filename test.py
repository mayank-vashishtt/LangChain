import pymongo
from config import ConfigData
import dns.resolver  # MongoDB Atlas requires this for SRV records

print("Testing connection...")
try:
    client = pymongo.MongoClient(
        ConfigData.MONGO_DB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000
    )
    
    # Force a connection to verify it works
    client.admin.command('ping')
    
    # Try accessing your specific database and collection
    db = client[ConfigData.DB_NAME]
    collection = db[ConfigData.COLLECTION_NAME]
    
    # Try a simple query
    doc_count = collection.count_documents({})
    print(f"Connection successful! Found {doc_count} documents in collection.")
    
except pymongo.errors.ConfigurationError as e:
    print("MongoDB Atlas DNS resolution error:", e)
except pymongo.errors.ConnectionError as e:
    print("MongoDB connection error:", e)
except Exception as e:
    print("Other error:", e)