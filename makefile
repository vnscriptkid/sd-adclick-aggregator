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

up_kafka:
	docker compose up -d zoo1 kafka1 kafka2 kafka3 manager redis

ui_kafka:
	open http://localhost:9000
	
topic_create:
	docker compose exec kafka1 kafka-topics \
		--create \
		--topic impressions \
		--partitions 3 \
		--replication-factor 3 \
		--if-not-exists \
		--bootstrap-server kafka1:19092

topic_describe:
	docker exec -it kafka1 kafka-topics \
		--describe \
		--topic impressions \
		--bootstrap-server kafka1:19092

# describe consumer group
group_describe:
	docker exec -it kafka1 kafka-consumer-groups \
		--describe \
		--group impression_counter \
		--bootstrap-server kafka1:19092

# list all consumer groups
consumer_groups:
	docker exec -it kafka1 kafka-consumer-groups \
		--list \
		--bootstrap-server kafka1:19092

topic_consume:
	docker exec -it kafka1 kafka-console-consumer \
		--topic impressions \
		--from-beginning \
		--property print.key=true \
		--property print.partition=true \
		--property print.offset=true \
		--bootstrap-server kafka1:19092

redis_cli:
	docker compose exec redis redis-cli