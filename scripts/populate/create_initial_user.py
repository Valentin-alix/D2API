from pathlib import Path
import sys
from dotenv import get_key

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.const import ENV_PATH
from src.database import SessionMaker
from src.models.user import User


def create_initial_user():
    username = get_key(ENV_PATH, "SUPERUSER_USERNAME")
    password = get_key(ENV_PATH, "SUPERUSER_PASSWORD")
    session = SessionMaker()
    if session.query(User).filter(User.email == username).one_or_none() is None:
        session.add(User(email=username, password=password))
        session.commit()


if __name__ == "__main__":
    create_initial_user()
