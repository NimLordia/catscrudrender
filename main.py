# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
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

def get_client_ip(request: Request) -> str:
    """
    Get the real client IP from request headers or direct connection.
    Handles cases where the request comes through a proxy.
    """
    # Check for X-Forwarded-For header (used by most proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, first one is the original client
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header (used by some proxies)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # If no proxy headers, use the direct client IP
    return request.client.host if request.client else "Unknown"

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
origins = [
    "https://nimlordia.github.io",
    # Add localhost for testing if needed
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Log request details with IP
    logger.info(f"""
    Request:
    - Timestamp: {datetime.now().isoformat()}
    - Client IP: {client_ip}
    - Method: {request.method}
    - URL: {request.url}
    - User-Agent: {request.headers.get('user-agent', 'Unknown')}
    - Origin: {request.headers.get('origin', 'Unknown')}
    - Headers: {dict(request.headers)}
    """)
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(f"""
        Response:
        - Client IP: {client_ip}
        - Status: {response.status_code}
        - Process Time: {process_time:.3f}s
        - Headers: {dict(response.headers)}
        """)
        
        return response
    except Exception as e:
        logger.error(f"""
        Error processing request:
        - Client IP: {client_ip}
        - Error: {str(e)}
        - URL: {request.url}
        - Method: {request.method}
        """)
        raise

# CRUD Operations
@app.post("/cats/")
async def create_cat(cat: CatCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    logger.info(f"Creating new cat from IP: {client_ip}, Data: {cat.dict()}")
    try:
        db_cat = CatDB(**cat.dict())
        db.add(db_cat)
        db.commit()
        db.refresh(db_cat)
        logger.info(f"Successfully created cat with ID: {db_cat.id} from IP: {client_ip}")
        return db_cat
    except Exception as e:
        logger.error(f"Error creating cat from IP {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cats/")
async def read_cats(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    logger.info(f"Fetching cats from IP: {client_ip} with skip={skip}, limit={limit}")
    try:
        cats = db.query(CatDB).offset(skip).limit(limit).all()
        logger.info(f"Successfully fetched {len(cats)} cats for IP: {client_ip}")
        return cats
    except Exception as e:
        logger.error(f"Error fetching cats for IP {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cats/{cat_id}")
async def delete_cat(cat_id: int, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    logger.info(f"Attempting to delete cat with ID: {cat_id} from IP: {client_ip}")
    try:
        db_cat = db.query(CatDB).filter(CatDB.id == cat_id).first()
        if db_cat is None:
            logger.warning(f"Cat with ID {cat_id} not found for deletion (requested from IP: {client_ip})")
            raise HTTPException(status_code=404, detail="Cat not found")
        
        db.delete(db_cat)
        db.commit()
        logger.info(f"Successfully deleted cat {cat_id} (requested from IP: {client_ip})")
        return {"message": "Cat deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting cat {cat_id} from IP {client_ip}: {str(e)}")
        raise

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)