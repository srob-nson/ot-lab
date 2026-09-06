FROM python:3

RUN pip install --no-cache-dir bacpypes3

COPY device.py /device.py

CMD ["python", "-u", "/device.py"]
