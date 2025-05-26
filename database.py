from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "scheduler_db"

# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections
users_collection = db.users
events_collection = db.events
constraints_collection = db.constraints

async def init_db():
    # Check if users exist
    if await users_collection.count_documents({}) == 0:
        # Add 5 users with unique constraints
        users = [
            {
                "name": "Alice",
                "timezone": "US/Eastern",
                "availability": [
                    {"day": "Monday", "start": "09:00", "end": "17:00"},
                    {"day": "Wednesday", "start": "13:00", "end": "17:00"}
                ]
            },
            {
                "name": "Bob",
                "timezone": "US/Pacific",
                "availability": [
                    {"day": "Tuesday", "start": "10:00", "end": "18:00"},
                    {"day": "Wednesday", "start": "14:00", "end": "18:00"}
                ]
            },
            {
                "name": "Carol",
                "timezone": "Europe/London",
                "availability": [
                    {"day": "Wednesday", "start": "13:00", "end": "17:00"},
                    {"day": "Thursday", "start": "09:00", "end": "12:00"}
                ]
            },
            {
                "name": "Dave",
                "timezone": "Asia/Tokyo",
                "availability": [
                    {"day": "Monday", "start": "08:00", "end": "12:00"},
                    {"day": "Friday", "start": "15:00", "end": "18:00"}
                ]
            },
            {
                "name": "Eve",
                "timezone": "US/Central",
                "availability": [
                    {"day": "Wednesday", "start": "13:00", "end": "17:00"},
                    {"day": "Friday", "start": "09:00", "end": "12:00"}
                ]
            }
        ]
        await users_collection.insert_many(users)

        # Add constraints
        constraints = [
            {
                "user_id": 1,
                "preferred_times": [{"day": "Wednesday", "start": "13:00", "end": "17:00"}],
                "unavailable_slots": [{"day": "Monday", "start": "12:00", "end": "13:00"}],
                "capacity": 3
            },
            {
                "user_id": 2,
                "preferred_times": [{"day": "Tuesday", "start": "10:00", "end": "12:00"}],
                "unavailable_slots": [{"day": "Wednesday", "start": "15:00", "end": "16:00"}],
                "capacity": 2
            },
            {
                "user_id": 3,
                "preferred_times": [{"day": "Thursday", "start": "09:00", "end": "12:00"}],
                "unavailable_slots": [{"day": "Wednesday", "start": "14:00", "end": "15:00"}],
                "capacity": 2
            },
            {
                "user_id": 4,
                "preferred_times": [{"day": "Friday", "start": "15:00", "end": "18:00"}],
                "unavailable_slots": [{"day": "Monday", "start": "09:00", "end": "10:00"}],
                "capacity": 1
            },
            {
                "user_id": 5,
                "preferred_times": [{"day": "Friday", "start": "09:00", "end": "12:00"}],
                "unavailable_slots": [{"day": "Wednesday", "start": "16:00", "end": "17:00"}],
                "capacity": 2
            }
        ]
        await constraints_collection.insert_many(constraints)

        # Add 10 events (some overlapping)
        now = datetime.now(pytz.timezone('US/Eastern'))
        events = [
            {
                "title": "Team Sync",
                "start": now + timedelta(days=1, hours=13),
                "end": now + timedelta(days=1, hours=14),
                "priority": 1,
                "participants": ["Alice", "Bob"]
            },
            {
                "title": "Project Kickoff",
                "start": now + timedelta(days=2, hours=14),
                "end": now + timedelta(days=2, hours=15),
                "priority": 2,
                "participants": ["Carol", "Dave"]
            },
            {
                "title": "Design Review",
                "start": now + timedelta(days=3, hours=13),
                "end": now + timedelta(days=3, hours=14),
                "priority": 1,
                "participants": ["Alice", "Carol"]
            },
            {
                "title": "Client Call",
                "start": now + timedelta(days=1, hours=13, minutes=30),
                "end": now + timedelta(days=1, hours=14, minutes=30),
                "priority": 3,
                "participants": ["Bob", "Eve"]
            },
            {
                "title": "1:1 Alice-Bob",
                "start": now + timedelta(days=4, hours=10),
                "end": now + timedelta(days=4, hours=11),
                "priority": 2,
                "participants": ["Alice", "Bob"]
            },
            {
                "title": "1:1 Carol-Dave",
                "start": now + timedelta(days=5, hours=9),
                "end": now + timedelta(days=5, hours=10),
                "priority": 2,
                "participants": ["Carol", "Dave"]
            },
            {
                "title": "All Hands",
                "start": now + timedelta(days=6, hours=15),
                "end": now + timedelta(days=6, hours=16),
                "priority": 1,
                "participants": ["Alice", "Bob", "Carol", "Dave", "Eve"]
            },
            {
                "title": "Retrospective",
                "start": now + timedelta(days=7, hours=13),
                "end": now + timedelta(days=7, hours=14),
                "priority": 2,
                "participants": ["Dave", "Eve"]
            },
            {
                "title": "Planning",
                "start": now + timedelta(days=8, hours=11),
                "end": now + timedelta(days=8, hours=12),
                "priority": 1,
                "participants": ["Bob", "Carol", "Eve"]
            },
            {
                "title": "Brainstorm",
                "start": now + timedelta(days=9, hours=14),
                "end": now + timedelta(days=9, hours=15),
                "priority": 3,
                "participants": ["Alice", "Dave"]
            }
        ]
        await events_collection.insert_many(events) 