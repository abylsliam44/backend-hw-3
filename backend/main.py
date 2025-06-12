from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from . import models, schemas, auth
from .database import engine, get_db, SessionLocal
from .agents.gemini_agent import GeminiAgent
from .agents.conversation_manager import ConversationManager
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS with environment-based origins
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize conversation manager and agents
conversation_manager = ConversationManager(max_turns=5)  # Reduced to 5 turns for demo

# Initialize Gemini agents with different personalities
agent_a = GeminiAgent(
    api_key=os.getenv("GOOGLE_API_KEY", ""),
    name="Agent A",
    personality="You are a curious and enthusiastic AI who loves learning new things and asking thoughtful questions."
)

agent_b = GeminiAgent(
    api_key=os.getenv("GOOGLE_API_KEY", ""),
    name="Agent B",
    personality="You are a knowledgeable and analytical AI who enjoys explaining complex topics in simple terms."
)

conversation_manager.add_agent(agent_a)
conversation_manager.add_agent(agent_b)

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/categories/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_category = models.Category(**category.dict(), user_id=current_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[schemas.Category])
def get_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_transaction = models.Transaction(**transaction.dict(), user_id=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=List[schemas.Transaction])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# WebSocket endpoint for agent conversation
@app.websocket("/ws/conversation")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Get initial prompt from client
        initial_data = await websocket.receive_text()
        initial_prompt = initial_data

        # Start conversation
        async for response in conversation_manager.start_conversation(initial_prompt):
            # Send each response to the client
            await websocket.send_json(response)
            
            # Add a delay between messages for better readability
            await asyncio.sleep(2)

        # Send conversation complete message
        await websocket.send_json({
            "agent": "System",
            "message": "Conversation complete",
            "timestamp": "",
            "type": "end"
        })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "agent": "System",
            "message": f"Error: {str(e)}",
            "timestamp": "",
            "type": "error"
        })

# Endpoint to get conversation history
@app.get("/conversation/history")
async def get_conversation_history():
    return conversation_manager.get_conversation_history()

# Endpoint to export conversation
@app.get("/conversation/export")
async def export_conversation():
    return {"conversation": conversation_manager.export_conversation()} 