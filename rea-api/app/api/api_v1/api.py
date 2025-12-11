from fastapi import APIRouter

from .endpoints import metadata, properties, equipment, geo

api_router = APIRouter()
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])
