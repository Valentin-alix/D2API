import os
from pathlib import Path
import sys

from sqlalchemy.orm import Session


sys.path.append(os.path.join(Path(__file__).parent.parent.parent.parent))

from scripts.populate.extern.populate_config_user import populate_configs
from scripts.populate.extern.populate_user import create_initial_users
from src.database import SessionMaker


def populate_extern(session: Session):
    create_initial_users(session)
    populate_configs(session)


if __name__ == "__main__":
    with SessionMaker() as session:
        populate_extern(session)
