# Python 3.10 ishlatamiz
FROM python:3.10-slim

# Konteyner ichidagi ishchi katalog
WORKDIR /app

# Kutubxonalarni o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko‘chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]
