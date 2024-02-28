# ultron
Repo to ai-engine


## run on local
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

## run using docker
```bash
docker-compose up;
```

## sample .env file
```
OPENAI_API_KEY="sk-<key-here>"
POSTGRES_USER=wiyseuser
POSTGRES_PASSWORD=12345
POSTGRES_SERVER=host.docker.internal
POSTGRES_PORT=5433
POSTGRES_DB=wiyse
EMBEDDINGS_MODEL_NAME=all-MiniLM-L6-v2
PGVECTOR_VECTOR_SIZE=384
SIMILARITY_THRESHOLD=0.6
DOCUMENT_CHUNK_SIZE = 500
DOCUMENT_CHUNK_OVERLAP = 50
```


## payload for generate intro endpoint
```json
{
    "app_name_domain": "Hubspot, CRM/Marketing/Outreach",
    "basic_info": "CRM for SME's",
    "feature": "you can manage marketing, sales, ticketing operations",
    "capability": "benefits companies to gain leads, close deals, generate revenue with proper invoicing."
}
```