from api.database.database import session
from api.database.models import UserDB, DataSourceDB, ViewDB, ChartDB
from api.models.user import User

from typing import List


def insert_new_user(customer: User):
    session.rollback()
    try:
        session.add(customer)
        session.commit()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
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
        session.remove()
    if user:
        return user
    

def get_all_users() -> List[UserDB]:
    try:
        users = session.query(UserDB).all()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if users:
        return users


def get_data_sources_by_user_id(user_id: int) -> List[DataSourceDB]:
    try:
        data_sources = (
            session.query(DataSourceDB)
            .filter(
                DataSourceDB.user_id == user_id
            ).order_by(DataSourceDB.id)
            .all()
        )
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if data_sources:
        return data_sources
    

def get_data_source_by_airbyte_source_id(source_id: str) -> DataSourceDB:
    try:
        data_sources = (
            session.query(DataSourceDB)
            .filter(
                DataSourceDB.airbyte_source_id == source_id
            )
            .first()
        )
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if data_sources:
        return data_sources
    


    
def get_data_sources_by_id(data_source_id: int) -> DataSourceDB:
    try:
        data_source = session.query(DataSourceDB).filter(DataSourceDB.id == data_source_id).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if data_source:
        return data_source
    

def get_view_by_id(view_id: int) -> ViewDB:
    try:
        view = session.query(ViewDB).filter(ViewDB.id == view_id).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if view:
        return view


def get_views_by_user_id(user_id: int) -> List[DataSourceDB]:
    try:
        data_sources = session.query(ViewDB).filter(ViewDB.user_id == user_id).all()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if data_sources:
        return data_sources


def get_chart_by_chart_id(chart_id) -> ChartDB:
    try:
        chart = session.query(ChartDB).filter(ChartDB.chart_id == chart_id).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
        session.remove()
    if chart:
        return chart