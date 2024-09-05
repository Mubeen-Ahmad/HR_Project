# from fastapi import FastAPI, Depends, HTTPException, status, Request
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import RedirectResponse, HTMLResponse
# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime, timedelta
# import jwt
# import uvicorn
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from dotenv import load_dotenv
# import os


# # load_dotenv()
# # SECRET_KEY = os.environ.get("SECRET_KEY", None)
# # ALGORITHM = os.environ.get("ALGORITHM", None)
# # ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
# # ALGORITHM = os.environ.get("ALGORITHM", None)
# # REFRESH_TOKEN_EXPIRE_DAYS = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)


# # Configuration
# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60
# REFRESH_TOKEN_EXPIRE_DAYS = 7


# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Dummy database
# users_db = {
#     "admin": {"username": "admin", "password": "admin", "role": "admin"},
#     "hr_user": {"username": "hr_user", "password": "hr_password", "role": "hr"},
# }


# # Models
# class User(BaseModel):
#     username: str
#     role: str


# class UserCreate(BaseModel):
#     username: str
#     password: str
#     role: str


# # Token generation
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# # Dependencies
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         user = users_db.get(username)
#         if user is None:
#             raise credentials_exception
#         return user
#     except jwt.PyJWTError:
#         raise credentials_exception


# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = users_db.get(form_data.username)
#     if not user or user["password"] != form_data.password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#         )
#     access_token = create_access_token(
#         data={"sub": user["username"], "role": user["role"]}
#     )
#     refresh_token = create_refresh_token(
#         data={"sub": user["username"], "role": user["role"]}
#     )
#     response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
#     response.set_cookie(key="access_token", value=access_token, httponly=True, path="/")
#     response.set_cookie(
#         key="refresh_token", value=refresh_token, httponly=True, path="/"
#     )
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


# # @app.get("/create-hr-user", response_class=HTMLResponse)
# # async def create_hr_user_page(request: Request, token: str = Depends(oauth2_scheme)):
# #     token_data = get_current_user(token)

# #     if token_data["role"] != "admin":
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
# #         )
# #     return HTMLResponse(
# #         content=open("templates/create_hr_user.html").read(), status_code=200
# #     )


# @app.get("/create-hr-user", response_class=HTMLResponse)
# async def create_hr_user_page(request: Request):
#     token = request.cookies.get("access_token")
#     token_data = get_current_user(token)

#     if token_data["role"] != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#         )
#     return templates.TemplateResponse("create_hr_user.html", {"request": request})


# @app.post("/post_create-hr-user/")
# def post_create_hr_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
#     token_data = get_current_user(token)

#     #     if token_data["role"] != "admin":
#     #         raise HTTPException(
#     #             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#     #         )
#     #     if user.role != "hr":
#     #         raise HTTPException(
#     #             status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'hr'"
#     #         )

#     if user.username in users_db:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
#         )
#     users_db[user.username] = {
#         "username": user.username,
#         "password": user.password,
#         "role": user.role,
#     }
#     return {"msg": "User created successfully"}


# @app.post("/launch-complaint/")
# def launch_complaint(description: str, token: str = Depends(oauth2_scheme)):
#     token_data = get_current_user(token)
#     if token_data["role"] != "hr":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#         )
#     # Store complaint in a dummy database
#     return {"msg": "Complaint submitted successfully"}


# @app.get("/view-complaints/")
# def view_complaints(token: str = Depends(oauth2_scheme)):
#     token_data = get_current_user(token)
#     if token_data["role"] != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#         )
#     # Return complaints from a dummy database
#     return {
#         "complaints": [
#             {"description": "Sample complaint", "timestamp": "2024-09-01T12:00:00"}
#         ]
#     }


# @app.get("/")
# async def index(request: Request):
#     token = request.cookies.get("access_token")
#     if token:
#         user = get_current_user(token)
#         role = user.get("role") if user else None
#         return templates.TemplateResponse(
#             "index.html", {"request": request, "user_role": role}
#         )
#     else:
#         return templates.TemplateResponse(
#             "index.html", {"request": request, "user_role": None}
#         )


# @app.get("/login")
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})


# @app.get("/logout")
# def logout():
#     response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
#     response.delete_cookie(key="access_token")
#     response.delete_cookie(key="refresh_token")
#     return response


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
