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
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.exchange_declare(exchange='toworker', exchange_type='direct')

# Initialize the Flask application
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)



@app.route('/apiv1/analyze', methods=[ 'POST'])
def analyze():
    r = request 
    message = json.loads(r.data)
    print(message)
    message = message['sentences']
    #print(message[0])
    toWorkerKey = "sentimentanalysis"
    for m in message:
        #logging info to rabbitmq
        rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/analyze attempted for sentence " + m)

        rabbitMQChannel.basic_publish(
            exchange='toworker', routing_key=toWorkerKey, body=m)
        print(" [x] Sent %r:%r" % (toWorkerKey, m))
        time.sleep(3)
        
    response = {'action' : 'queued' }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/apiv1/cache/sentiment', methods=[ 'GET'])
def cache():
    #logging info to rabbitmq
    rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/cache attempted " )
    print("cache end point:")

    try:
        print("entered try block")
        sentiment =  "sentiment_analysis_results"
        response = redisClient.smembers(sentiment)
        print(response)
        response1 = list(response)
        res2 = []
        for x in response1:
            res3 = codecs.decode(x)
            res2.append(res3)
        #response2 = codecs.decode(response1[0])
        #logging info to rabbitmq
        rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/cache attempt succeeded" )
    except:
        #logging info to rabbitmq
        rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/cache query failed")

    #response
    response = {'model': "sentiment", 'analysis': res2}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/apiv1/sentence', methods=[ 'GET'])
def sentence():
    message = json.loads(request.data)
    print(message)
    sentiment =  "sentiment_analysis_results"
    message = message['sentences']
    response = []

    try:
        for sentence in message:
            # read from the redis
            print("entered try block")
            result = redisClient.smembers(sentiment)
            print(result)
            result = list(result)
            print ("inside Loop")
            
            
            for x in result:
                y = codecs.decode(x)
                print(y)
                if sentence in y:
                    print("innner loop " + y)
                    response.append(y)
        rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/sentence: response fetched" + response )
    except:
        rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/sentence: error" )
        


    #logging info to rabbitmq
    rabbitMQChannel.basic_publish(
            exchange='logs', routing_key=infoKey, body="/apiv1/sentence attempted " )

    #response
    response = {'model' :  'sentiment', 'analysis' : response }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/', methods=['GET'])
def hello():
    return '<h1> Sentiment Server</h1><p> Use a valid endpoint </p>'


# start flask app
app.run(host="0.0.0.0", port=5000)
rabbitMQ.close()
##
## Your code goes here..
##


