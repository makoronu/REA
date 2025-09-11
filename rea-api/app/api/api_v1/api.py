from fastapi import APIRouter
from .endpoints import properties, metadata

api_router = APIRouter()
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])