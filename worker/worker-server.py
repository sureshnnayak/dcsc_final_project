#
# Worker server
#
import pickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests
import time

from datetime import date
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

from sklearn.preprocessing import MinMaxScaler



hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db = redis.Redis(host=redisHost, db=1)         
stockType1 = "abc"
stockType2 = "pqr"
stockType3 = "xyz"    
currentDate = date.today()                                                             

##
## Set up rabbitmq connection
##


rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

redisClient = redis.Redis(host=redisHost, port=6379, db=0)

rabbitMQChannel.queue_declare(queue='toWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
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

##
## Your code goes here...
##



def stockPrediction(stockType, currentOpenValue):
    #setting the training data - There are three types of training data - StockTypes 1,2,3
    TrainFileName1 = stockType1+".csv"
    TrainFileName2 = stockType2+".csv"
    TrainFileName3 = stockType3+".csv"
    training_data1 = pd.read_csv(TrainFileName1)
    training_data2 = pd.read_csv(TrainFileName2)
    training_data3 = pd.read_csv(TrainFileName3)
    if(stockType == stockType1):
        training_data = training_data1
    elif(stockType == stockType2):
        training_data = training_data2
    elif(stockType == stockType3):
        training_data = training_data3



    training_data.shape
    training_data = training_data.iloc[:, 1:2]
    print("Training data raw: \n", training_data)
    print("Type of training data: ", type(training_data))
    training_data.shape
    training_data.head()
    mm = MinMaxScaler(feature_range = (0, 1))
    training_data = mm.fit_transform(training_data)
    print("Length of training data before x,y split: ", len(training_data))
    length = len(training_data)
    #x_train = training_data[0:1257]
    x_train = training_data[0:(length-1)]
    #y_train = training_data[1:1258]
    y_train = training_data[1:length]

    #print(x_train.shape)
    #print(y_train.shape)
    x_train = np.reshape(x_train, (1257, 1, 1))

    #print(x_train.shape)

    # initializing the model
    model = Sequential()

    # adding the input layer and the LSTM layer
    model.add(LSTM(units = 4, activation = 'sigmoid', input_shape = (None, 1)))

    # adding the output layer
    model.add(Dense(units = 1))

    # compiling the model
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')

    # fitting the RNN to the training data
    model.fit(x_train, y_train, batch_size = 32, epochs = 220)

    real_stock_price = currentOpenValue
    print("Test data: ", real_stock_price)
    #real_stock_price.head()

    inputs = real_stock_price
    inputs = mm.transform(inputs)
    #inputs = np.reshape(inputs, (20, 1, 1))


    predicted_stock_price = model.predict(inputs)
    predicted_stock_price = mm.inverse_transform(predicted_stock_price)
    result = predicted_stock_price

    #print("predicted values: \n", predicted_stock_price)
    return result

#myCall = stockPrediction("Stock_type")
#print("Predicted value: \n", myCall)


#routing key  
toWorkerKey = "stockPredictionKey"

rabbitMQChannel.exchange_declare(exchange='toworker', exchange_type='direct')
result = rabbitMQChannel.queue_declare(queue=toWorkerKey, exclusive=True)
queue_name = result.method.queue


#bind the queue
rabbitMQChannel.queue_bind(
            exchange='toworker', queue=queue_name, routing_key=toWorkerKey)

def callback(ch, method, properties, body):
    message = body.decode()
    print(" [x] %r:%r" % (method.routing_key, message))
    # push the content to redis
    stock = message["stockType"]
    openPrice = message["openPriceCurrentDate"]
    result = stockPrediction(stock, openPrice)
    print(result)
    resDict = dict()
    resDict["currentDate"] = str(currentDate)
    resDict["predictedValueNextDay"] = str(result)
    myStr = str(resDict)
    time.sleep(3)
    # Adding current date and predicted value for next day as one entry to particular type of set named 'stockType' in Redis
    redisClient.sadd(stock, myStr)

    # Printing set entries of a particular stocktype
    print("Contents of the Redis set:")
    print(redisClient.smembers(stock))


print(' [*] Waiting for logs. To exit press CTRL+C')
rabbitMQChannel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()