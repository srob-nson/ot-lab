FROM python:3

RUN pip install --no-cache-dir pymodbus==3.11.3

COPY hmi.py /hmi.py

CMD ["python", "-u", "/hmi.py"]
