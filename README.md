# Mędrzec AI

## Setup

Optional: Create a virtual environment

```
python -m venv venv
```

Configure required environment variables

- copy `.env.example` to `.env`
- fill in environment variables

Install dependencies

```
pip install -U -r requirements.txt
```

Run database migrations

```
alembic upgrade head
```

Run the project

```
uvicorn medrzec_ai.__main__:app
```

You may want to update the Pinecone database

```
python update_pinecone.py "./Remote Work Playbook.md"
```
