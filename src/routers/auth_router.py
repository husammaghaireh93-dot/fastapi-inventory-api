"""
Auth endpoints: Register, Login, Me.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from ..schemas import UserRegister, UserLogin, TokenResponse
from ..auth import create_access_token, get_current_user
from ..crud import create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: UserRegister):
    user_id = create_user(req.username, req.password, req.role or "user")
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully", "user_id": user_id, "username": req.username}

@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"], "user_id": user["id"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "username": user["username"], "role": user["role"]}  # nosec B105

@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return user
