from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.customer import User

engine=create_engine("postgresql://vizo:devpassword@postgres:5432/vizo",
)

Base=declarative_base()

SessionLocal=sessionmaker(bind=engine)

session = SessionLocal()


def insert_new_user(customer: User):
    session.rollback()
    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer
