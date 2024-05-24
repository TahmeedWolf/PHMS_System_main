FROM python:3.10.11
EXPOSE 5000/tcp
WORKDIR /api
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]