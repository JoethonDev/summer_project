from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://admin:admin@label.ik9njat.mongodb.net/?retryWrites=true&w=majority&appName=Label"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
db = client.label

collection = db['labels']