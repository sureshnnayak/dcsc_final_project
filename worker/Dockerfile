FROM python


RUN /usr/local/bin/python -m pip install --upgrade pip
RUN  pip install flask pika redis requests jsonpickle Pillow numpy panda keras tensorflow
WORKDIR /srv
COPY  worker-server-all.py /srv
COPY  INFY.csv /srv
COPY  TCS.csv /srv
COPY  SBIN.csv /srv



#ENV	FLASK_PORT 5000
EXPOSE 5001

CMD	["python", "worker-server-all.py"]