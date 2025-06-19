FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sync_google_drive.py ./
COPY credentials.json ./

VOLUME ["/data"]
VOLUME ["/consume"]

CMD ["python", "sync_google_drive.py"]