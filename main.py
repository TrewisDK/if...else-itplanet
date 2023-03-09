from fastapi import APIRouter

from database import Base, engine
from endpoints import account, animals, locations, registration, animals_types, animals_visited_locations

Base.metadata.create_all(bind=engine)

api_router = APIRouter()

api_router.include_router(account.router, prefix="/accounts")
api_router.include_router(animals.router, prefix='/animals')
api_router.include_router(locations.router, prefix="/locations")
api_router.include_router(registration.router, prefix="/registration")
api_router.include_router(animals_types.router, prefix='/animals/types')
api_router.include_router(animals_visited_locations.router, prefix='/animals/{animalId}/locations')
