up:
	docker compose up --build -d spark-master spark-worker-1 spark-worker-2 
	sleep 10
	docker compose up jupyter

down:
	docker compose down --remove-orphans --volumes

spark:
	open http://localhost:8080

jupyter_log:
	docker compose exec jupyter bash -c "logs"

logs_master:
	docker compose logs spark-master -f

cli_master:
	docker compose exec spark-master bash

cli_jupyter:
	docker compose exec jupyter bash

spark_kafka:
	docker compose exec spark-master sh -c "pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1"