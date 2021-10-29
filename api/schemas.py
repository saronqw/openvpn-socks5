from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List


class ConfigurationBase(BaseModel):
    filename: str


class Configuration(ConfigurationBase):
    id: int

    class Config:
        orm_mode = True


class Container(BaseModel):
    id: str
    ports: Dict
    status: str
    started_at: datetime
    finished_at: datetime
    ovpn_file: str


class ContainerList(BaseModel):
    containers: List[Container]
