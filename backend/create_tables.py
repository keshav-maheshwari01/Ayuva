from app.database import Base , engine 
from app import model

Base.metadata.create_all(bind = engine)