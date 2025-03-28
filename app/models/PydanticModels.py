from pydantic import BaseModel, Field, EmailStr

class SigninUser(BaseModel):
    username: str = Field(min_length=1, description="Username for the system")
    password: str = Field(min_length=8, description="User password")

class SignupUser(SigninUser):
    name: str = Field(min_length=1, description="User actual name")
    email: EmailStr = Field(description="User email")

class Provider(BaseModel):
    provider: str = Field(description="Database provider")

class Metadata(BaseModel):
    metadata: list[str] = Field(description="Metadata of database")

class DBConnectionDetails(Provider):
    uri: str = Field(description="Database URI")

class DBMetadataDetails(Provider, Metadata):
    pass

class DBQuery(DBConnectionDetails):
    query: str = Field(description="Database query")

class AIQuery(Provider, Metadata):
    query: str = Field(description="Human readable query")
