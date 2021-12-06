FROM python:3.9.1

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN  pip install flask pika redis requests jsonpickle Pillow numpy pandas keras sklearn
RUN pip install tensorflow
# RUN pip install https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.8.0-py3-none-any.whl 
WORKDIR /srv
COPY  worker-server.py /srv
COPY  INFY.csv /srv
COPY  TCS.csv /srv
COPY  SBIN.csv /srv



#ENV	FLASK_PORT 5000
EXPOSE 5001


CMD	["python3", "worker-server.py"]
