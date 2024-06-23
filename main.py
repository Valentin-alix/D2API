import os
from pathlib import Path
from time import sleep

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from src.database import run_migrations
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
    world
)

app = FastAPI()

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


if __name__ == "__main__":
    os.system(
        f"docker-compose -f {os.path.join(Path(__file__).parent, "docker-compose.dev.yml")} up -d"
    )
    sleep(3)
    run_migrations()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
