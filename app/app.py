from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from mangum import Mangum
import os
import json

db_config_json = os.getenv("DB_CONFIG_JSON")
if db_config_json:
    config = json.loads(db_config_json)
else:
    config = {
        "host": os.getenv("HOST"),
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "port": os.getenv("PORT"),
        "dbname": os.getenv("DBNAME"),
    }

db_url = URL.create(
    drivername="mysql+pymysql",
    host=config["host"],
    username=config["username"],
    password=config["password"],
    port=config["port"],
    database=config["dbname"]
)

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSchema(BaseModel):
    id: str
    name: str

@app.get("/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user")
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(id=user.id, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User Created"}

@app.put("/user/{user_id}")
def update_user(user_id: str, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db.commit()
    return {"message": "User Updated"}

@app.delete("/user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User Deleted"}

handler = Mangum(app, lifespan="off")