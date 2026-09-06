FROM python:3

RUN pip install --no-cache-dir pymodbus

COPY client.py /client.py

CMD ["python", "-u", "/client.py"]
