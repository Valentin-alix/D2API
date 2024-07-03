import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
import socket
import sys
from time import sleep

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from scripts.populate.extern.populate_extern import populate_extern
from src.database import SessionMaker, run_migrations
from src.routers import (
    user,
    breed,
    character,
    collectable,
    item,
    job,
    map,
    price,
    recipe,
    server,
    spell,
    sub_area,
    template,
    type_item,
    world,
    login,
    config_user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    populate_extern(SessionMaker())
    yield


app = FastAPI(lifespan=lifespan)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger.info("API is starting.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(character.router)
app.include_router(breed.router)
app.include_router(collectable.router)
app.include_router(item.router)
app.include_router(job.router)
app.include_router(map.router)
app.include_router(price.router)
app.include_router(recipe.router)
app.include_router(server.router)
app.include_router(spell.router)
app.include_router(sub_area.router)
app.include_router(type_item.router)
app.include_router(world.router)
app.include_router(template.router)
app.include_router(login.router)
app.include_router(config_user.router)


def is_db_ready(host: str, port: int) -> bool:
    """Vérifie si la base de données est prête pour les connexions."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


if __name__ == "__main__":
    os.system(
        f"docker-compose -f {os.path.join(Path(__file__).parent, "docker-compose.dev.yml")} up -d"
    )
    while not is_db_ready("localhost", 5432):
        sleep(1)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
