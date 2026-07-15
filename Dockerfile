# Optional containerised run. Build: docker build -t owkin-agent .
# Run interactively:  docker run -it --env-file .env owkin-agent
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
