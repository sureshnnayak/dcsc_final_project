FROM python:3.8


RUN /usr/local/bin/python -m pip install --upgrade pip
RUN  pip3 install flask pika redis requests jsonpickle Pillow
WORKDIR /srv
COPY  worker-server-all.py /srv
COPY  INFY.csv /srv
COPY  TCS.csv /srv
COPY  SBIN.csv /srv



#ENV	FLASK_PORT 5000
EXPOSE 5001

CMD	["python3", "worker-server-all.py"]