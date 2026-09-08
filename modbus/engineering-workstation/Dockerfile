FROM python:3

RUN pip install --no-cache-dir pymodbus==3.11.3

COPY client.py /client.py

CMD ["python", "-u", "/client.py"]
