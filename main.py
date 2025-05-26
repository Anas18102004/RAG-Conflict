from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import init_db, users_collection, events_collection, constraints_collection
from models import User, Event, Constraint, TimeSlot
import pandas as pd
import os
import io
from datetime import datetime
import httpx
from dotenv import load_dotenv
from bson import ObjectId
import pytz
import json

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Replace with actual DeepSeek API endpoint

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.post("/upload")
async def upload_schedule(file: UploadFile = File(...)):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith('.json'):
            df = pd.read_json(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        # Convert DataFrame to list of dictionaries
        events = []
        for _, row in df.iterrows():
            event = {
                "title": row['title'],
                "start": pd.to_datetime(row['start']),
                "end": pd.to_datetime(row['end']),
                "priority": int(row['priority']),
                "participants": [name.strip() for name in row['participants'].split(',')]
            }
            events.append(event)
        
        # Insert events into MongoDB
        if events:
            await events_collection.insert_many(events)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conflicts")
async def get_conflicts():
    try:
        # Simple conflict detection based on overlapping events
        events = await events_collection.find().to_list(length=None)
        conflicts = []
        
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if (event1['start'] < event2['end'] and event1['end'] > event2['start']):
                    # Check if there are common participants
                    common_participants = set(event1['participants']) & set(event2['participants'])
                    if common_participants:
                        conflicts.append({
                            "event1": event1,
                            "event2": event2,
                            "common_participants": list(common_participants)
                        })
        
        return {"conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_schedule(request: Request):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
        
    data = await request.json()
    query = data.get('query', '')
    
    try:
        # Extract participants and requirements from the query using DeepSeek
        async with httpx.AsyncClient() as client:
            # First, analyze the query to extract participants and requirements
            analysis_prompt = f"""Analyze the following scheduling request and extract:
1. List of participants (names)
2. Required resources (rooms, equipment, etc.)
3. Time constraints or preferences
4. Any other specific requirements

Request: {query}

Provide the information in JSON format."""

            analysis_response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            )
            
            if analysis_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error analyzing request")
            
            analysis = analysis_response.json()
            
            # Get all events from the database
            events = await events_collection.find().to_list(length=None)
            
            # Find conflicts based on the analysis
            conflicts = []
            for i, event1 in enumerate(events):
                for event2 in events[i+1:]:
                    # Check for time conflicts
                    if (event1['start'] < event2['end'] and event1['end'] > event2['start']):
                        # Check for participant conflicts
                        common_participants = set(event1['participants']) & set(event2['participants'])
                        if common_participants:
                            conflicts.append({
                                "event1": event1,
                                "event2": event2,
                                "common_participants": list(common_participants)
                            })
            
            # Generate suggestions using DeepSeek
            suggestion_prompt = f"""Based on the following information, provide scheduling suggestions:

Original Request: {query}

Analysis: {analysis}

Detected Conflicts: {conflicts}

Please provide:
1. Conflict Analysis
2. Suggested Time Slots
3. Resource Recommendations
4. Alternative Solutions"""

            suggestion_response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": suggestion_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if suggestion_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error generating suggestions")
            
            suggestions = suggestion_response.json()
            
            return {
                "conflicts": conflicts,
                "analysis": analysis,
                "suggestions": suggestions
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    query: str
    is_scheduling_query: bool = False

@app.post("/chat")
async def chat(request: ChatRequest):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
    
    try:
        # If it's a scheduling query, use the existing analyze-query logic
        if request.is_scheduling_query:
            return await analyze_query(QueryRequest(query=request.query))
        
        # For general questions, use DeepSeek directly
        async with httpx.AsyncClient() as client:
            chat_prompt = f"""You are a helpful AI assistant that can help with both general questions and scheduling tasks.
The user can ask you about anything, and you can also help them schedule meetings and manage their calendar.

Current query: {request.query}

Provide a clear, concise, and informative response. If the user is asking about your capabilities,
mention that you can help with both general questions and scheduling tasks.

Remember:
1. Be friendly and conversational
2. For greetings, introduce yourself and explain your capabilities
3. For questions about your capabilities, explain both your chat and scheduling features
4. For general knowledge questions, provide accurate and helpful information
5. If you're not sure about something, be honest about it

Your response:"""

            response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": chat_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error generating response")
            
            # Debug the response
            print("DeepSeek API Response:", response.json())
            
            # Extract the response text from the DeepSeek API response
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message", {})
                content = message.get("content", "I apologize, but I couldn't generate a proper response.")
            else:
                content = "I apologize, but I couldn't generate a proper response."
            
            return {
                "response": content,
                "type": "chat"
            }
            
    except Exception as e:
        print("Error in chat endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-query")
async def analyze_query(request: QueryRequest):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
    
    try:
        print(f"Received query: {request.query}")  # Debug log
        
        # First, determine if this is a scheduling query or a general question
        async with httpx.AsyncClient() as client:
            query_type_prompt = f"""Analyze this query and determine if it's a scheduling-related question or a general question.
Query: {request.query}

Consider the following:
1. Greetings (hi, hello, hey) are general questions
2. Questions about scheduling, meetings, availability are scheduling queries
3. General knowledge questions are general questions
4. Questions about the system's capabilities are general questions

Respond with a JSON object:
{{
    "is_scheduling_query": true/false,
    "confidence": 0-1,
    "reason": "explanation"
}}"""

            query_type_response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": query_type_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            )
            
            if query_type_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error analyzing query type")
            
            # Debug the response
            print("Query Type Response:", query_type_response.json())
            
            query_type_data = query_type_response.json()
            if "choices" in query_type_data and len(query_type_data["choices"]) > 0:
                message = query_type_data["choices"][0].get("message", {})
                query_type = message.get("content", {})
                try:
                    query_type = json.loads(query_type)
                except:
                    print("Failed to parse query type response:", query_type)
                    query_type = {"is_scheduling_query": False, "confidence": 0.5, "reason": "Failed to parse response"}
            else:
                print("No choices in query type response")
                query_type = {"is_scheduling_query": False, "confidence": 0.5, "reason": "No response from API"}
            
            print("Parsed query type:", query_type)  # Debug log
            
            # If it's not a scheduling query, handle it as a general question
            if not query_type.get("is_scheduling_query", False):
                # For greetings, provide a more friendly response
                if any(greeting in request.query.lower() for greeting in ['hi', 'hello', 'hey', 'greetings']):
                    response = {
                        "type": "chat",
                        "response": "Hello! I'm your AI assistant. I can help you schedule meetings or answer general questions. What would you like to do?"
                    }
                    print("Sending greeting response:", response)  # Debug log
                    return response
                
                # For other general questions
                chat_response = await chat(ChatRequest(query=request.query, is_scheduling_query=False))
                print("Sending chat response:", chat_response)  # Debug log
                return chat_response

            # Continue with scheduling query analysis
            events = await events_collection.find().to_list(length=None)
            constraints = await constraints_collection.find().to_list(length=None)
            
            analysis_prompt = f"""Analyze this scheduling request and extract key information:
Request: {request.query}

Available Events: {events}
Constraints: {constraints}

Extract:
1. Participants
2. Time preferences/constraints
3. Duration
4. Priority level
5. Any special requirements

Format the response as JSON with these fields:
{{
    "participants": [],
    "time_preferences": [],
    "duration": "",
    "priority": 1-5,
    "special_requirements": []
}}"""

            analysis_response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            )
            
            if analysis_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error analyzing request")
            
            analysis = analysis_response.json()
            print("Analysis response:", analysis)  # Debug log
            
            # Generate scheduling suggestions
            suggestion_prompt = f"""Based on this analysis, provide scheduling suggestions:

Analysis: {analysis}

Available Events: {events}
Constraints: {constraints}

Provide a response in this JSON format:
{{
    "suggested": [
        {{
            "time": "YYYY-MM-DD HH:MM",
            "duration": "HH:MM",
            "confidence": 0-1,
            "reason": "explanation"
        }}
    ],
    "conflicts": [
        {{
            "time": "YYYY-MM-DD HH:MM",
            "reason": "explanation"
        }}
    ],
    "alternatives": [
        {{
            "time": "YYYY-MM-DD HH:MM",
            "reason": "explanation"
        }}
    ],
    "rationale": "Overall explanation of the suggestions"
}}"""

            suggestion_response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": suggestion_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if suggestion_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error generating suggestions")
            
            suggestions = suggestion_response.json()
            suggestions["type"] = "scheduling"
            print("Sending scheduling response:", suggestions)  # Debug log
            return suggestions
            
    except Exception as e:
        print("Error in analyze_query:", str(e))  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# API Models
class EventCreate(BaseModel):
    title: str
    start: datetime
    end: datetime
    priority: int
    participants: List[str]

class EventResponse(EventCreate):
    id: str

# API Routes
@app.get("/users")
async def get_users():
    users = await users_collection.find().to_list(length=None)
    return [User(**user) for user in users]

@app.get("/events")
async def get_events():
    events = await events_collection.find().to_list(length=None)
    return [Event(**event) for event in events]

@app.get("/constraints")
async def get_constraints():
    constraints = await constraints_collection.find().to_list(length=None)
    return [Constraint(**constraint) for constraint in constraints]

@app.post("/events", response_model=EventResponse)
async def create_event(event: EventCreate):
    # Convert to dict and remove None values
    event_dict = event.dict(exclude_none=True)
    
    # Insert into MongoDB
    result = await events_collection.insert_one(event_dict)
    
    # Get the created event
    created_event = await events_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for response
    created_event["id"] = str(created_event.pop("_id"))
    
    return created_event

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    try:
        event = await events_collection.find_one({"_id": ObjectId(event_id)})
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        event["id"] = str(event.pop("_id"))
        return event
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    try:
        result = await events_collection.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event deleted successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

@app.put("/events/{event_id}")
async def update_event(event_id: str, event: EventCreate):
    try:
        event_dict = event.dict(exclude_none=True)
        result = await events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": event_dict}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        updated_event = await events_collection.find_one({"_id": ObjectId(event_id)})
        updated_event["id"] = str(updated_event.pop("_id"))
        return updated_event
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID") 