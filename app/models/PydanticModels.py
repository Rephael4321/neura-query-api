from pydantic import BaseModel, Field, EmailStr

class SigninUser(BaseModel):
    username: str = Field(min_length=1, description="Username for the system")
    password: str = Field(min_length=8, description="User password")

class SignupUser(SigninUser):
    name: str = Field(min_length=1, description="User actual name")
    email: EmailStr = Field(description="User email")

class URI(BaseModel):
    uri: str = Field(description="Database URI")

class DBConnectionDetails(URI):
    provider: str = Field(description="Database provider")

class DBQuery(URI):
    query: str = Field(description="Database query")

class AIQuery(BaseModel):
    query: str = Field(description="Human readable query")
