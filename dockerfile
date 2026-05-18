FROM python:3.11-alpine

WORKDIR /app


RUN addgroup -S appgroup && adduser -S appuser -G appgroup


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN chown -R appuser:appgroup /app


USER appuser

EXPOSE 5000


CMD ["python", "app.py"]
