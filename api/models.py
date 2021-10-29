from sqlalchemy import Column, Integer, String

from database import Base


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
