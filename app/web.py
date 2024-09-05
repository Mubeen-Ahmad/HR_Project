from fastapi import FastAPI, Request, Depends, status, HTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import jwt
from typing import Optional
from datetime import datetime, timedelta

from pydantic import BaseModel

from dotenv import load_dotenv
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ===================================================================
# SECRECTS

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY", None)
ALGORITHM = os.environ.get("ALGORITHM", None)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
ALGORITHM = os.environ.get("ALGORITHM", None)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7))


# =====================================================================
# DUMMY DB
users_db = {
    "admin": {"username": "admin", "password": "admin", "role": "admin"},
    "hr": {"username": "hr", "password": "hr", "role": "hr"},
}


# ==================================================================
# MODELS
class User(BaseModel):
    username: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


# ===================================================================
# functionality


# active highlight link
def is_active(request: Request, link: str) -> str:
    return "active" if request.url.path == link else ""


# check current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = users_db.get(username)
        if user is None:
            raise credentials_exception
        return user
    except jwt.PyJWTError:
        raise credentials_exception


# create tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==================================================================
# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get("access_token")
    if token:

        try:
            user = get_current_user(token)


            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "is_active": is_active,
                    "user_role": user.get("role"),
                    "username": user.get("username"),
                },
            )

        except Exception as e:

            return templates.TemplateResponse(
                "login.html",
                {"request": request, "user_role": None, "is_active": is_active},
            )

    return templates.TemplateResponse(
        "login.html", {"request": request, "user_role": None, "is_active": is_active}
    )


@app.post("/token")
def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):  # Added request parameter
    user = users_db.get(form_data.username)

    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, path="/")
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, path="/"
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.get("/login")
async def login_page(request: Request):

    token = request.cookies.get("access_token")

    if token:
        try:
            user = get_current_user(token)

            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "is_active": is_active,
                    "user_role": user.get("role"),
                },
            )

        except Exception as e:

            return templates.TemplateResponse(
                "login.html",
                {"request": request, "user_role": None, "is_active": is_active},
            )

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user_role": None, "is_active": is_active},
    )


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response


@app.get("/create_hr_user", response_class=HTMLResponse)
async def create_hr_user(request: Request):

    token = request.cookies.get("access_token")
    token_data = get_current_user(token)

    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return templates.TemplateResponse(
        "create_hr_user.html",
        {"request": request, "user_role": "admin", "is_active": is_active},
    )


@app.post("/post_create-hr-user/")
def post_create_hr_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
    token_data = get_current_user(token)

    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    users_db[user.username] = {
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }
    return {"msg": "User created successfully"}
