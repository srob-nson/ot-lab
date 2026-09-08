FROM python:3

RUN pip install --no-cache-dir bacpypes3==0.0.106

COPY device.py /device.py

CMD ["python", "-u", "/device.py"]
