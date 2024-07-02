from src.models.user import ConfigUser, User
from src.queries.user import populate_config


from sqlalchemy.orm import Session


def populate_configs(session: Session):
    """used at user creation"""
    for user_id in session.query(User.id).all():
        if (
            session.query(ConfigUser)
            .filter(ConfigUser.user_id == user_id[0])
            .one_or_none()
            is None
        ):
            populate_config(session, user_id[0])
