FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt
COPY . .
ENTRYPOINT ["python", "-m", "medrzec-ai"]
