from pydantic import BaseModel
from typing import List


class TypeGroupAdvertise(BaseModel):
    title: str
    token: str

    class Config:
        orm_mode = True


class TypeGroupsAdvertise(BaseModel):
    __root__: List[TypeGroupAdvertise]


class TypeAdvertise(BaseModel):
    filename: str

    class Config:
        orm_mode = True


class TypeAdvertiseList(BaseModel):
    __root__: List[TypeAdvertise]

    class Config:
        orm_mode = True
