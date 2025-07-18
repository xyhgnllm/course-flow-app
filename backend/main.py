
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import passlib.hash as _hash
import jwt as _jwt
import datetime

# --- Configuration ---
JWT_SECRET = "a_very_secret_key_for_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# --- FastAPI App Initialization ---
app = FastAPI()

# Mount static files directory
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# --- In-Memory Database ---
# Using dictionaries to simulate database tables
db_users = {}
db_courses = {}
db_purchases = {}

# --- Sample Data ---
def populate_sample_data():
    global db_courses, db_users
    python_videos = []
    for i in range(1, 21):
        python_videos.append(
            {"id": 100 + i, "title": f"1-{i}: Python基础知识点 {i}", "price": 5, "preview_url": "https://www.w3schools.com/html/mov_bbb.mp4"}
        )

    db_courses = {
        1: {"id": 1, "name": "Python入门基础", "price": 128, "videos": python_videos},
        2: {"id": 2, "name": "Vue.js从零到一", "price": 128, "videos": [
            {"id": 201, "title": "2-1：初识Vue", "price": 5, "preview_url": "https://www.w3schools.com/html/mov_bbb.mp4"},
            {"id": 202, "title": "2-2：组件化开发", "price": 5, "preview_url": "https://www.w3schools.com/html/mov_bbb.mp4"},
        ]}
    }
    # Create a sample user
    hashed_password = _hash.pbkdf2_sha256.hash("123456")
    db_users["testuser"] = {
        "username": "testuser", 
        "hashed_password": hashed_password,
        "balance": 99.9,
        "download_count": 0
    }

populate_sample_data()


# --- Pydantic Models (Data Schemas) ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Purchase(BaseModel):
    item_type: str  # 'video' or 'category'
    item_id: int

class Video(BaseModel):
    id: int
    title: str
    price: int
    preview_url: str

class Course(BaseModel):
    id: int
    name: str
    price: int
    videos: List[Video]

class User(BaseModel):
    username: str
    balance: float
    download_count: int
    purchases: List[Dict]

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# CORS Middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"], # Expose headers
)


# --- Utility Functions ---
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = _jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in db_users:
            raise credentials_exception
        token_data = TokenData(username=username)
    except _jwt.PyJWTError:
        raise credentials_exception
    return db_users[token_data.username]


# --- API Endpoints ---
@app.get("/api/courses", response_model=List[Course])
async def get_courses():
    return list(db_courses.values())

@app.post("/api/register")
async def register_user(user: UserCreate):
    if user.username in db_users:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = _hash.pbkdf2_sha256.hash(user.password)
    db_users[user.username] = {
        "username": user.username, 
        "hashed_password": hashed_password,
        "balance": 100.0, # Starting balance
        "download_count": 0
    }
    # After registration, create a token and log the user in
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/login")
async def login_for_access_token(user: UserLogin):
    db_user = db_users.get(user.username)
    if not db_user or not _hash.pbkdf2_sha256.verify(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # Return user info and their purchases
    username = current_user['username']
    user_purchases = db_purchases.get(username, [])
    return {
        "username": username, 
        "purchases": user_purchases,
        "balance": current_user.get("balance", 0),
        "download_count": current_user.get("download_count", 0)
    }


@app.post("/api/purchase")
async def purchase_item(purchase: Purchase, current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    if username not in db_purchases:
        db_purchases[username] = []

    # Check for duplicates
    for p in db_purchases[username]:
        if p['item_type'] == purchase.item_type and p['item_id'] == purchase.item_id:
            raise HTTPException(status_code=400, detail="You have already purchased this item.")
    
    db_purchases[username].append(purchase.dict())
    return {"message": "Purchase successful!", "purchase": purchase}


@app.get("/api/download/{video_id}")
async def get_download_link(video_id: int, current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    user_purchases = db_purchases.get(username, [])

    has_access = False
    video_to_download = None
    category_id_of_video = None

    # Find the video and its category
    for cat_id, category in db_courses.items():
        for video in category['videos']:
            if video['id'] == video_id:
                video_to_download = video
                category_id_of_video = cat_id
                break
        if video_to_download:
            break
    
    if not video_to_download:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check purchase records
    for p in user_purchases:
        # Check if the specific video was purchased
        if p['item_type'] == 'video' and p['item_id'] == video_id:
            has_access = True
            break
        # Check if the entire category was purchased
        if p['item_type'] == 'category' and p['item_id'] == category_id_of_video:
            has_access = True
            break

    if not has_access:
        raise HTTPException(status_code=403, detail="You have not purchased this item.")

    # In a real app, this would generate a secure, temporary link to a file in cloud storage
    db_users[username]["download_count"] += 1
    # Return a FileResponse to force download
    file_path = "videos/sample_video.mp4"
    return FileResponse(path=file_path, media_type='application/octet-stream', filename=f"{video_to_download['title']}.mp4")


@app.post("/api/users/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    user_in_db = db_users.get(username)

    if not _hash.pbkdf2_sha256.verify(request.current_password, user_in_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long",
        )

    hashed_password = _hash.pbkdf2_sha256.hash(request.new_password)
    db_users[username]["hashed_password"] = hashed_password
    return {"message": "Password changed successfully"}

