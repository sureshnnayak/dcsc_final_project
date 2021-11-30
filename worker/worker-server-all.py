#
# Worker server
#
import pickle
import platform
import io
import os
import sys
import jsonpickle
import pika
import redis
import hashlib
import json
import requests
import time

from flair.models import TextClassifier
from flair.data import Sentence


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

sentiment =  "sentiment_analysis_results"

print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db = redis.Redis(host=redisHost, db=1)                                                                           

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
redisClient = redis.Redis(host=redisHost, port=6379, db=0)
infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)
def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)


##
## Your code goes here...
##

def analyze(message):
    classifier = TextClassifier.load('sentiment')
    sentence = Sentence(message)
    classifier.predict(sentence)
    result = sentence.to_dict('sentiment')
    #print(result)
    return result

#routing key  
toWorkerKey = "sentimentanalysis"

rabbitMQChannel.exchange_declare(exchange='toworker', exchange_type='direct')
result = rabbitMQChannel.queue_declare(queue=toWorkerKey, exclusive=True)
queue_name = result.method.queue

while(redisClient.scard(sentiment) > 0):
    redisClient.spop(sentiment)


#bind the queue
rabbitMQChannel.queue_bind(
            exchange='toworker', queue=queue_name, routing_key=toWorkerKey)

def callback(ch, method, properties, body):
    message = body.decode()
    print(" [x] %r:%r" % (method.routing_key, message))
    # push the content to redis
    result = analyze(message)
    print(result)
    result1 = str(result)
    time.sleep(3)
    redisClient.sadd(sentiment, result1)

    # adding dummy responce 
    #redisClient.sadd(sentiment, result2)
    print("Contents of the Redis set:")
    print(redisClient.smembers(sentiment))


print(' [*] Waiting for logs. To exit press CTRL+C')
rabbitMQChannel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()