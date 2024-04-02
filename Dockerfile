FROM python:3.12-slim
LABEL authors="hekzory"

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot/__init__.py"]
