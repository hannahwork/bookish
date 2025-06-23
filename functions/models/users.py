import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    date_of_birth: Optional[datetime.date] = None