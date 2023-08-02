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
    try:
        user = session.query(UserDB).filter(UserDB.email == email).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
    if user:
        return user


def get_data_sources_by_user_id(user_id: int) -> List[DataSourceDB]:
    try:
        data_sources = (
            session.query(DataSourceDB).filter(DataSourceDB.user_id == user_id).all()
        )
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
    if data_sources:
        return data_sources
