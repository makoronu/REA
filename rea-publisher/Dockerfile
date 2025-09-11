FROM python:3.11-slim

WORKDIR /app

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーション
COPY . .

CMD ["python", "src/main.py"]
