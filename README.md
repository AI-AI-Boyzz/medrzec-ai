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

Run the API

```
python -m medrzec-ai
```

Run the Slack bot

```
python -m slack-bot
```

You may want to update the Pinecone database

```
python update_pinecone.py "./Remote-First Work Playbook.md"
```
