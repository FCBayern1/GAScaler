FROM python:3.9-slim

WORKDIR /app

COPY exponential_test.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "exponential_test.py"]
