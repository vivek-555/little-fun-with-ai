from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    filename: str
    context_name: str
    content: str
    embeddings: list[float] | None = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int

    class Config:
        orm_mode = True

class DocumentCreated(BaseModel):
    id: int
    filename: str
    context_name: str
    content: str

class SimilarDocumentResult(BaseModel):
    id: int
    filename: str
    context_name: str
    simlarity: float
    created_at: str
    updated_at: str
