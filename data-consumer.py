import argparse

from kafka import KafkaConsumer

def consume(topic_name, kafka_broker):
	consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_broker)

	for message in consumer:
		print(message)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('topic_name', help='the kafka topic to pull from')
	parser.add_argument('kafka_broker', help='the location of the kafka broker')

	# Parse arguments
	args = parser.parse_args()
	topic_name = args.topic_name
	kafka_broker = args.kafka_broker

	consume(topic_name, kafka_broker)