from fastapi import APIRouter

from .endpoints import metadata, properties, equipment, geo, admin, zoho, touki, flyer

api_router = APIRouter()
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(zoho.router, prefix="/zoho", tags=["zoho"])
api_router.include_router(touki.router, prefix="/touki", tags=["touki"])
api_router.include_router(flyer.router, prefix="/flyer", tags=["flyer"])
