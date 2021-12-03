
docker build -t "worker" .
docker tag TAG sureshnnayak/stockprediction-worker
docker push sureshnnayak/stockprediction-worker

