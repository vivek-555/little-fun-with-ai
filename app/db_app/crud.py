from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_document(db: Session, context_name: str, file_name: str):
    return db.query(models.Document).filter(models.Document.context_name == context_name, models.Document.filename==file_name).first()

def delete_document(db: Session, document: schemas.Document):
    db.delete(document)
    db.commit()
    return True

def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def create_documents(db: Session, documents: list[schemas.DocumentCreate]):
    db_documents = list(map(lambda d: models.Document(**d.dict()), documents))
    db.add_all(db_documents)
    db.commit()
    map(lambda db_doc: db.refresh(db_doc), db_documents)    # refresh fills the generated id
    return db_documents

def update_document(db: Session, document: schemas.Document):
    db_document = models.Document(**document.dict())
    db.merge(db_document)
    db.commit()
    return db_document

# work in progress - not working yet
def get_similar_documents(db: Session, similarity_threshold: float, embed_query: list[float]):
    return db.query(models.Document).filter(1 - models.Document.embeddings.cosine_distance(embed_query) > similarity_threshold).order_by(models.Document.embeddings.cosine_distance(embed_query)).first()
