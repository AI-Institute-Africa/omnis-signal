from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.api_key import ApiKey
from datetime import datetime
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    master_key = os.getenv("MASTER_API_KEY", "dev-master-key")
    
    if not api_key_header:
        # For development ease, if no key is provided and master key is default, allow
        if master_key == "dev-master-key":
            return "master"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
        )
        
    # Check master key
    if api_key_header == master_key:
        return "master"
        
    # Check DB
    api_key = db.query(ApiKey).filter(ApiKey.key == api_key_header, ApiKey.is_active == True).first()
    if api_key:
        api_key.last_used = datetime.utcnow()
        db.commit()
        return api_key.owner

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate API KEY",
    )
