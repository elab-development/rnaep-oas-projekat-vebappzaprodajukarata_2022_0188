import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("MONGO_DB")]

email_logs = db["email_logs"]