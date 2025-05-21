from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

UsersBase = declarative_base()
RequestsBase = declarative_base()

class User(UsersBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    login = relationship("Login", back_populates="user", cascade="all, delete-orphan", uselist=False)
    uris = relationship("Uri", back_populates="user", cascade="all, delete-orphan")

class Login(UsersBase):
    __tablename__ = "logins"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="login")

class Uri(UsersBase):
    __tablename__ = "uris"

    id = Column(Integer, primary_key=True)
    uri = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="uris")

class JWT(RequestsBase):
    __tablename__ = "jwt"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    username = Column(Text, nullable=False)
    jwt = Column(Text, nullable=True)
    has_uri = Column(Boolean, nullable=True, default=False)
    status = Column(Text, nullable=False)
    failure_reason = Column(Text, nullable=True)

class DBConnection(RequestsBase):
    __tablename__ = "db_connection"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    uri = Column(String, nullable=True)
    status = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)

class DBResponse(RequestsBase):
    __tablename__ = "db_response"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    db_query = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    result_type = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)

class AIResponse(RequestsBase):
    __tablename__ = "ai_response"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    ai_query = Column(Text, nullable=False)
    responder = Column(Text, nullable=True)
    db_response_id = Column(Integer, nullable=True)
    response = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)
