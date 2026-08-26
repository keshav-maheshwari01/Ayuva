from passlib.context import CryptContext 

import os 
from jose import jwt 
from datetime import datetime , timedelta
from dotenv import load_dotenv

load_dotenv()

pwd_content = CryptContext(schemes = ["bcrypt"] , deprecated = "auto")

def hashing(password : str) -> str : 
    return pwd_content.hash(password)

def verify_password(plain_password : str , hashed_password : str ) -> bool : 
    return pwd_content.verify(plain_password , hashed_password)



SECRET_KEY = "some-long-random-secret"
ALGORITHM = "HS256"

def create_access_token(data : dict ,expires_delta : timedelta  = timedelta(hours= 24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)


    

