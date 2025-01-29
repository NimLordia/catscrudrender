# main.py
from fastapi import Request

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

# Update CRUD operations to include IP logging
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