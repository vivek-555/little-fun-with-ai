import os
from functools import lru_cache
import requests
import json
from typing import Union, Annotated
from helper import load_single_document, LOADER_MAPPING

import config

from fastapi import FastAPI, Depends, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from langchain.llms import OpenAIChat
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.embeddings import HuggingFaceEmbeddings
from typing import Any, Optional
from entities.intro import Intro

from db_app import crud, models, schemas
from db_app.database import SessionLocal, engine

# this is a temporary fix for the pgvector library issue
# more information at: https://github.com/hwchase17/langchain/pull/3964
os.environ["PGVECTOR_VECTOR_SIZE"] = "384"

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "https://www.wiyse.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OpenAIWrapper(ChatOpenAI):
    client: Optional[Any] = None

@lru_cache()
def get_settings():
    return config.Settings()

@app.get("/chatgptold/{message}")
def connect_to_chatgpt(message: str, q: Union[str, None] = None):
    url = "https://api.openai.com/v1/chat/completions"
    payload = json.dumps({
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": message
        }
      ],
      "temperature": 0.7
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    return {"message": response.text}

# define post endpoint called generate_intro that takes 4 body params 
# (app_name_domain, basic_info, feature, capability) and create prompt using these parameters and hit openai api to get response
@app.post("/generate_intro")
def generate_intro(intro: Intro, settings: Annotated[config.Settings, Depends(get_settings)]):

    raw_application_data = f"""Application Intro:
        1. Application Name & domain: {intro.app_name_domain}
        2. Basic intro of application: {intro.basic_info}
        3. what does it do? {intro.feature}
        4. Whom does it benefit and how? {intro.capability}
    """

    prompt_multiple = PromptTemplate(
        input_variables=["raw_app_data"],
        template="""Take raw application Intro data & generate new intro into 3 following sentences keeping title. 
                            (a) Application Intro Sentence:
                            (b) What does this application do?: 
                            (c) Overall benefits of application: 
                            
                    Raw application Intro data: {raw_app_data}"""
        )

    prompt_multiple.format(raw_app_data=raw_application_data)
    llm = OpenAIWrapper(model="gpt-3.5-turbo", openai_api_key=settings.openai_api_key)
    llm_chain = LLMChain(prompt=prompt_multiple, llm=llm)
    output = llm_chain.predict(raw_app_data = raw_application_data)

    return output

# users endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.post('/upload_document', response_model=list[schemas.DocumentCreated])
def upload_doc(uploadedFile: UploadFile, context_name: str,  settings: Annotated[config.Settings, Depends(get_settings)], db: Session = Depends(get_db)):
    filename = str(uploadedFile.filename)
    ext = "." + filename.rsplit(".", 1)[-1]
    if filename == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No selected file',
        )
    if ext not in LOADER_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f'File {uploadedFile.filename} has unsupported extension type',
        )

    save_path = os.path.join('../source_documents', filename)
    with open(save_path, "wb+") as file_object:
        file_object.write(uploadedFile.file.read())

    # Load documents and split in chunks
    print(f"Loading file document {filename}")
    document = load_single_document(save_path)
    text = document.page_content
    print(f"Loaded {len(text)} long document from {filename}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    texts = text_splitter.split_text(text)

    # Create embeddings
    embedding_client = HuggingFaceEmbeddings(model_name=settings.embeddings_model_name)
    
    db_document = crud.get_document(db, context_name, filename)
    if db_document is not None:
        print(f"Deleting all documents with filename:{filename} and context_name: {context_name}")
        crud.delete_document(db, db_document)

    print(f"Creating new documents with filename:{filename} and context_name: {context_name}")
    documents: list[schemas.DocumentCreate] = []
    
    for txt in texts:
        embeddings = embedding_client.embed_query(txt)
        documents.append(schemas.DocumentCreate(filename=filename, context_name=context_name, content=txt, embeddings=embeddings))

    documents_latest = crud.create_documents(db=db, documents=documents)
    documents_result = list(map(lambda d: schemas.DocumentCreated(id=d.id, filename=str(d.filename), context_name=str(d.context_name), content=str(d.content)) , documents_latest)) # type: ignore - hack
    return documents_result

@app.post('/return_document', response_model=schemas.Document)
def return_document(query: str, settings: Annotated[config.Settings, Depends(get_settings)], db: Session = Depends(get_db)):
    embedding_client = HuggingFaceEmbeddings(model_name=settings.embeddings_model_name)
    embedding_query = embedding_client.embed_query(query)

    # find the relevant document in vector db using this embedding query
    db_document = crud.get_similar_documents(db, settings.similarity_threshold, embedding_query)
    if db_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'no match found for query "{query}"',
        )
    db_document.__setattr__('embeddings', list(map(lambda val: float(val), db_document.embeddings.tolist()))) # hack because serialization throws error
    return db_document
