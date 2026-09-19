from passlib.context import CryptContext 

import os 
from jose import jwt 
from datetime import datetime , timedelta
from dotenv import load_dotenv
from fastapi import Header , HTTPException , Depends

from pathlib import Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

pwd_content = CryptContext(schemes = ["bcrypt"] , deprecated = "auto")

def hashing(password : str) -> str : 
    return pwd_content.hash(password)

def verify_password(plain_password : str , hashed_password : str ) -> bool : 
    return pwd_content.verify(plain_password , hashed_password)


SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data : dict ,expires_delta : timedelta  = timedelta(hours= 24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)






def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(required_role : str ):
    def role_checker(current_user : dict = Depends(get_current_user)):
        if current_user.get("role") != required_role : 
            raise HTTPException(status_code = 403 , detail = f"{required_role} role required")
        return current_user 
    return role_checker 
