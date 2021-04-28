from pydantic import BaseModel
from typing import List


class TypeAdvertise(BaseModel):
    filename: str

    class Config:
        orm_mode = True


class TypeAdvertiseList(BaseModel):
    __root__: List[TypeAdvertise]

    class Config:
        orm_mode = True


class TypeGroupAdvertise(BaseModel):
    title: str
    token: str
    advertises: List[TypeAdvertise]

    class Config:
        orm_mode = True


class TypeGroupsAdvertise(BaseModel):
    __root__: List[TypeGroupAdvertise]
