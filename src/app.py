"""
High School Management System API

A simple FastAPI application for extracurricular activity signups
with user authentication and role-based access.
"""

import hashlib
import os
import secrets
from pathlib import Path
from typing import Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}

# In-memory attendance database
attendance: Dict[str, list] = {}
users: Dict[str, Dict[str, str]] = {}
sessions: Dict[str, str] = {}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    role: str


class ActivityCreateRequest(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int


class ActivityUpdateRequest(BaseModel):
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def require_roles(*allowed_roles: str):
    def _require_roles(current_user: Dict[str, str] = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _require_roles


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


def create_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    sessions[token] = email
    return token


def get_current_user(authorization: str = Header(None)) -> Dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ", 1)[1]
    email = sessions.get(token)
    if not email or email not in users:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"email": email, "role": users[email]["role"], "token": token}


def require_role(required_role: str):
    def _require_role(current_user: Dict[str, str] = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _require_role


@app.on_event("startup")
def startup_event():
    # Create a default admin user for management and testing.
    if "admin@mergington.edu" not in users:
        users["admin@mergington.edu"] = {
            "hashed_password": hash_password("admin123"),
            "role": "admin",
        }
    if "organizer@mergington.edu" not in users:
        users["organizer@mergington.edu"] = {
            "hashed_password": hash_password("organizer123"),
            "role": "organizer",
        }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/auth/register")
def register(request: RegisterRequest):
    email = request.email.lower()
    if email in users:
        raise HTTPException(status_code=400, detail="User already exists")

    role = request.role.lower() if request.role else "student"
    if role not in {"student", "organizer", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    if role != "student":
        raise HTTPException(status_code=403, detail="Cannot self-register as organizer or admin")

    users[email] = {
        "hashed_password": hash_password(request.password),
        "role": role,
    }
    token = create_token(email)

    return {"message": "Registration successful", "token": token, "email": email, "role": role}


@app.post("/auth/login")
def login(request: LoginRequest):
    email = request.email.lower()
    user = users.get(email)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(email)
    return {"message": "Login successful", "token": token, "email": email, "role": user["role"]}


@app.post("/auth/logout")
def logout(current_user: Dict[str, str] = Depends(get_current_user)):
    sessions.pop(current_user["token"], None)
    return {"message": "Logout successful"}


@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: Dict[str, str] = Depends(get_current_user)):
    return {"email": current_user["email"], "role": current_user["role"]}


@app.get("/activities")
def get_activities():
    # Include attendance info in the response
    result = {}
    for name, activity in activities.items():
        attended_count = len(attendance.get(name, []))
        result[name] = {**activity, "attended_count": attended_count}
    return result


@app.post("/activities")
def create_activity(
    request: ActivityCreateRequest,
    current_user: Dict[str, str] = Depends(require_roles("admin", "organizer")),
):
    activity_name = request.name.strip()
    if not activity_name:
        raise HTTPException(status_code=400, detail="Activity name must be provided")

    if activity_name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activities[activity_name] = {
        "description": request.description,
        "schedule": request.schedule,
        "max_participants": request.max_participants,
        "participants": [],
    }
    return {"message": f"Activity '{activity_name}' created successfully"}


@app.put("/activities/{activity_name}")
def update_activity(
    activity_name: str,
    request: ActivityUpdateRequest,
    current_user: Dict[str, str] = Depends(require_roles("admin", "organizer")),
):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if request.description is not None:
        activity["description"] = request.description
    if request.schedule is not None:
        activity["schedule"] = request.schedule
    if request.max_participants is not None:
        if request.max_participants < len(activity["participants"]):
            raise HTTPException(
                status_code=400,
                detail="Max participants cannot be less than current participant count",
            )
        activity["max_participants"] = request.max_participants

    return {"message": f"Activity '{activity_name}' updated successfully"}


@app.delete("/activities/{activity_name}")
def delete_activity(
    activity_name: str,
    current_user: Dict[str, str] = Depends(require_roles("admin", "organizer")),
):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activities.pop(activity_name)
    return {"message": f"Activity '{activity_name}' deleted successfully"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    current_user: Dict[str, str] = Depends(get_current_user),
    email: Optional[str] = None,
):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email and email.lower() != current_user["email"]:
        raise HTTPException(status_code=403, detail="Email does not match authenticated user")

    email = current_user["email"]
    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    current_user: Dict[str, str] = Depends(get_current_user),
    email: Optional[str] = None,
):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email and email.lower() != current_user["email"]:
        raise HTTPException(status_code=403, detail="Email does not match authenticated user")

    email = current_user["email"]
    activity = activities[activity_name]

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/activities/{activity_name}/checkin")
def checkin_to_activity(
    activity_name: str,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    """Check in to an activity (mark attendance)"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    email = current_user["email"]
    activity = activities[activity_name]

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="You must be signed up for this activity to check in")

    if activity_name not in attendance:
        attendance[activity_name] = []

    if email in attendance[activity_name]:
        raise HTTPException(status_code=400, detail="Already checked in to this activity")

    attendance[activity_name].append(email)
    return {"message": f"Checked in {email} to {activity_name}"}


@app.get("/activities/{activity_name}/attendance")
def get_activity_attendance(
    activity_name: str,
    current_user: Dict[str, str] = Depends(require_roles("admin", "organizer")),
):
    """Get attendance list for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    attended = attendance.get(activity_name, [])
    return {"activity": activity_name, "attended": attended, "count": len(attended)}
