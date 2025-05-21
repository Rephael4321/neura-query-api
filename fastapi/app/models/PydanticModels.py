from pydantic import BaseModel, Field, EmailStr

class SigninUser(BaseModel):
    username: str = Field(min_length=1, description="Username for the system")
    password: str = Field(min_length=8, description="User password")

class SignupUser(SigninUser):
    name: str = Field(min_length=1, description="User actual name")
    email: EmailStr = Field(description="User email")

class URI(BaseModel):
    uri: str | None = Field(description="Database URI")

class DBQuery(BaseModel):
    query: str = Field(description="Database query")

class AIQuery(BaseModel):
    query: str = Field(description="Human readable query")

class RequestStatus(BaseModel):
    record_id: int = Field(description="Record ID for which a status is required")
    topic_name: str = Field(description="Topic name for which a status is required")
