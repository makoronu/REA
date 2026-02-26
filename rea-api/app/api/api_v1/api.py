from fastapi import APIRouter

from .endpoints import metadata, properties, equipment, geo, admin, touki, registries, integrations, reinfolib, flyer, portal, auth, users, settings, images, scraper_sync

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(images.router, prefix="/properties", tags=["images"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(touki.router, prefix="/touki", tags=["touki"])
api_router.include_router(registries.router, tags=["registries"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(reinfolib.router, prefix="/reinfolib", tags=["reinfolib"])
api_router.include_router(flyer.router, prefix="/flyer", tags=["flyer"])
api_router.include_router(portal.router, prefix="/portal", tags=["portal"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(scraper_sync.router, prefix="/properties", tags=["scraper-sync"])
