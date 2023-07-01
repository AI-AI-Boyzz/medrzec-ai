FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt
COPY . .
ENTRYPOINT ["uvicorn", "medrzec-ai.__main__:app"]
EXPOSE 8000
