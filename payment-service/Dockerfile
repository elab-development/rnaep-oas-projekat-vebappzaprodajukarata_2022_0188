# Koristimo Python 3.13 kao baznu sliku
FROM python:3.13-slim

# Postavljamo radni direktorijum unutar kontejnera
WORKDIR /app

# Kopiramo requirements.txt u kontejner
COPY requirements.txt .

# Instaliramo zavisnosti
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo sve fajlove u kontejner
COPY . .

# Izlažemo port 8000
EXPOSE 8000

# Pokrecemo aplikaciju
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]