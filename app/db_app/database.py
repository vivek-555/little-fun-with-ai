from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config
import logging

settings = config.Settings()

database_url = f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_server}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(
    database_url
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# uncomment following code to see SQL queries in the console
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

Base = declarative_base()
