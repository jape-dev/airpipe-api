from api.database.database import session
from api.database.models import UserDB, DataSourceDB
from api.models.user import User

from typing import List


def insert_new_user(customer: User):
    session.rollback()
    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer


def get_user_by_email(email: str) -> UserDB:
    user = session.query(UserDB).filter(UserDB.email == email).first()

    return user


def get_data_sources_by_user_id(user_id: int) -> List[DataSourceDB]:
    data_sources = (
        session.query(DataSourceDB).filter(DataSourceDB.user_id == user_id).all()
    )

    return data_sources
