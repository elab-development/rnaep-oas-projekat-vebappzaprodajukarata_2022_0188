FROM python:3.12-slim

# Radni direktorijum
WORKDIR /app

# Sistemske zavisnosti (za pymysql / bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Instaliraj Python zavisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopira aplikaciju
COPY . .

# Port
EXPOSE 8000

# Pokreni server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
