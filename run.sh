docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq:3
pip3 install pika

docker pull redis
docker run -d -p 6379:6379 --name redis-server redis
pip3 install redis
