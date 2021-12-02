##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
#import hashlib,
import  requests
import json
import jsonpickle
import logging
import codecs
import time


##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

redisClient = redis.Redis(host=redisHost, port=6379, db=0)
print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db = redis.Redis(host=redisHost, db=1)



# setting up rabbitmq log's routing key names
infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost, heartbeat=0))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.exchange_declare(exchange='toworker', exchange_type='direct')

#routing keys  
toWorkerKey = "stockPredictionKey"
infoKey = "hostname.worker.info"
debugKey = "hostname.worker.debug"
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)
def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)


# Initialize the Flask application
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)



@app.route('/api/openprice', methods=[ 'POST'])
def analyze():
    r = request 
    message = json.loads(r.data)
    print(message)
    #message = message['stockname']
    #print(message[0])
    rabbitMQChannel.basic_publish(
        exchange='toworker', routing_key=toWorkerKey, body=message)
    
     

  
    response = {'SBI' : '481' }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/', methods=['GET'])
def hello():
    return Response(response='<h1> Sentiment Server</h1><p> Use a valid endpoint </p>', status=200)


# start flask app
app.run(host="0.0.0.0", port=5001)

##
## Your code goes here..
##


