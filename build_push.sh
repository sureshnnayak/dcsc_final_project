cd worker 
docker build -t "worker" .
docker tag TAG sureshnnayak/stockprediction-worker
docker push sureshnnayak/stockprediction-worker

cd ..
cd rest
docker build -t "rest" .
docker tag TAG sureshnnayak24/stockprediction-rest
docker push sureshnnayak24/stockprediction-rest

