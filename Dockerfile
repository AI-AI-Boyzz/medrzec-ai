FROM python:3.11-alpine
WORKDIR /app
RUN apk add g++
COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt
COPY . .
ENTRYPOINT sh -c "alembic upgrade head && uvicorn medrzec_ai.__main__:app --host 0.0.0.0 --port 80"
EXPOSE 80
