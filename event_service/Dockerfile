FROM python:3.13-slim

WORKDIR /app

COPY event_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY event_service/ .
COPY shared/ /app/shared/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]