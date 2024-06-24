from datetime import datetime
from dotenv import get_key


from src.const import ENV_PATH
from src.database import SessionMaker
from src.models.user import User


def create_initial_user():
    username = get_key(ENV_PATH, "SUPERUSER_USERNAME")
    password = get_key(ENV_PATH, "SUPERUSER_PASSWORD")
    if username is None or password is None:
        raise ValueError("Missing SUPERUSER_USERNAME or SUPERUSER_PASSWORD in .env")
    session = SessionMaker()
    superuser = session.query(User).filter(User.email == username).one_or_none()
    if superuser is None:
        session.add(
            User(email=username, password=password, sub_expire=datetime(3000, 1, 1))
        )
    else:
        superuser.email = username
        superuser.password = password
        superuser.sub_expire = datetime(3000, 1, 1)
    session.commit()
