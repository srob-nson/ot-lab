FROM python:3

RUN pip install --no-cache-dir bacpypes3==0.0.106

COPY client.py /client.py

CMD ["python", "-u", "/client.py"]
