from dotenv import get_key


from src.const import ENV_PATH
from src.database import SessionMaker
from src.models.user import User


def create_initial_users():
    su_username = get_key(ENV_PATH, "SUPERUSER_USERNAME")
    su_password = get_key(ENV_PATH, "SUPERUSER_PASSWORD")
    if su_username is None or su_password is None:
        raise ValueError("Missing SUPERUSER_USERNAME or SUPERUSER_PASSWORD in .env")
    session = SessionMaker()
    superuser = session.query(User).filter(User.email == su_username).one_or_none()
    if superuser is None:
        session.add(User(email=su_username, password=su_password, is_admin=True))
    else:
        superuser.email = su_username
        superuser.password = su_password
        superuser.is_admin = True

    an_username = get_key(ENV_PATH, "ANONYM_USERNAME")
    an_password = get_key(ENV_PATH, "ANONYM_PASSWORD")
    if an_username is None or an_password is None:
        raise ValueError("Missing ANONYM_USERNAME or ANONYM_PASSWORD in .env")
    session = SessionMaker()
    anonym = session.query(User).filter(User.email == an_username).one_or_none()
    if anonym is None:
        session.add(User(email=an_username, password=an_password))
    else:
        anonym.email = an_username
        anonym.password = an_password

    session.commit()
