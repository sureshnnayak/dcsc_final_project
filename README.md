# dcsc_final_project

## Team members:
- Anusha Basavaraja (anba9017@colorado.edu)
- Suresh N Nayak (suna7873@colorado.edu)

## Project Brief:
Deploying our project "Stock Open price Prediction as a Service" in kubernetes using components - REST front-end, RabbitMQ messaging, Redis database.

  Our service predicts the open price of stock for the next day given the stock name and open price of current date. Our service can now handle three stocks - Infosys(INFY), Tata Consultancy Services(TCS) and State Bank of India(SBIN). Our service uses the already loaded training data in the container to predict the next day open price of given stock. If we send wrong stock name in the request, the service will send an error message "Stock is not supported". Once the request is sent by the REST Client, REST Server will search in Redis database if the result is already present or not. If it finds the results, then REST Server will straight away fetch the result from Redis and sends back to REST Client as response. IF the result is not found in Redis database, then REST Server will log request into RabbitMQ message system which in turn triggers the worker. Then Worker will use the correct training dataset to predict the stock open price for the next day and upload it into Redis database which will be fetched by REST Server as response to REST Client.  
