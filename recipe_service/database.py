from motor.motor_asyncio import AsyncIOMotorClient

async def get_db():
    try:
        client = AsyncIOMotorClient("mongodb+srv://zyadamr:5734@gpdemo.0zqzfdo.mongodb.net/?retryWrites=true&w=majority&appName=gpdemo")
        print("Connected successfully")
        return client["gpdemo"]
    except Exception as e:
        print(f"An error occurred: {e}")
