from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    login = relationship("Login", back_populates="user", uselist=False)

class Login(Base):
    __tablename__ = "logins"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="login")

postgres_db_uri = "postgresql+psycopg2://myuser:mypassword@localhost:5432/postgres"

postgres_engine = create_engine(postgres_db_uri)

db_name = "neura_query"

create_db_query = f"CREATE DATABASE {db_name};"

with postgres_engine.connect() as connection:
    connection.execute(text("commit"))
    connection.execute(text(create_db_query))

neura_query_db_uri = "postgresql+psycopg2://myuser:mypassword@localhost:5432/neura_query"

neura_query_engine = create_engine(neura_query_db_uri)

Base.metadata.create_all(neura_query_engine)
