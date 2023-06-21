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

Run the project

```
uvicorn medrzec-ai.__main__:app
```

You may want to update the Pinecone database

```
python update_pinecone.py "./Remote Work Playbook.md"
```
