FROM python:3

RUN pip install --no-cache-dir cpppo==4.4.3

COPY cpppo.cfg /cpppo.cfg
COPY device.py /device.py

CMD ["python", "-u", "/device.py"]
