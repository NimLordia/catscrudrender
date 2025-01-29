# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from typing import List, Optional

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./cats.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Cat SQLAlchemy Model
class CatDB(Base):
    __tablename__ = "cats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    breed = Column(String)
    age = Column(Float)
    weight = Column(Float)

# Cat Pydantic Models
class CatBase(BaseModel):
    name: str
    breed: str
    age: float
    weight: float

class CatCreate(CatBase):
    pass

class Cat(CatBase):
    id: int
    
    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI app
app = FastAPI(title="Cats API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nimlordia.github.io/catsrenderfront/"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# CRUD Operations
@app.post("/cats/", response_model=Cat)
def create_cat(cat: CatCreate, db: Session = Depends(get_db)):
    db_cat = CatDB(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/cats/", response_model=List[Cat])
def read_cats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cats = db.query(CatDB).offset(skip).limit(limit).all()
    return cats

@app.get("/cats/{cat_id}", response_model=Cat)
def read_cat(cat_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(CatDB).filter(CatDB.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")
    return db_cat

@app.put("/cats/{cat_id}", response_model=Cat)
def update_cat(cat_id: int, cat: CatCreate, db: Session = Depends(get_db)):
    db_cat = db.query(CatDB).filter(CatDB.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    for key, value in cat.dict().items():
        setattr(db_cat, key, value)
    
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(CatDB).filter(CatDB.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    db.delete(db_cat)
    db.commit()
    return {"message": "Cat deleted successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)