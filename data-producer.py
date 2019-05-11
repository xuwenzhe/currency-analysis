# request API and save message to Kafka
import argparse
# release resource (thread pool, database connection, 
# network connection) once error occurs
import atexit
import json
import logging
import requests
import schedule
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger_format = "%(asctime)s - %(message)s"
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')
logger.setLevel(logging.DEBUG) # elaborate more details at debug level

API_BASE = 'https://api.gdax.com'


def check_symbol(symbol):
	"""
	Helper method checks if the symbol exists in coinbase API.
	"""
	logger.debug('Checking symbol.')
	try:
		response = requests.get(API_BASE + '/products')
		product_ids = [product['id'] for product in response.json()]
		if symbol not in product_ids:
			logger.warn('symbol %s not supported. The list of supported symbols: %s', symbol. product_ids)
			exit()
	except Exception as e:
		logger.warn('Failed to fetch products: %s', e)


def fetch_price(symbol, producer, topic_name):
	"""
	Helper function to retrieve data and send it to kafka
	"""
	logger.debug('Start to fetch prices for %s', symbol)
	try:
		# no ',' between text body and format
		response = requests.get('%s/products/%s/ticker' % (API_BASE, symbol))
		price = response.json()['price']

		timestamp = time.time()
		payload = {
			'Symbol': str(symbol),
			'LastTradePrice': str(price),
			'Timestamp': str(timestamp)
		}

		logger.debug('Retrieved %s info %s', symbol, payload)

		# serialization json => str, default string format is ASCII
		producer.send(topic=topic_name, value=json.dumps(payload).encode('utf-8'))
		logger.info('Sent price for %s to kafka', symbol)
	except Exception as e:
		logger.warn('Failed to fetch price: %s', e)


def shutdown_hook(producer):
	try:
		producer.flush(10) # forcely write buffer into disk, discard after 10 sec
	except KafkaError as kafka_error:
		logger.warn('Failed to Failed to flush pending messages to kafka, caused by: %s', kafka_error.message)
	finally:
		try:
			producer.close(10)
		except Exception as e:
			logger.warn('Failed to close kafka connection, cased by %s', e.message)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('symbol', help='the symbol you want to pull.')
	parser.add_argument('topic_name', help='the kafka topic push to.')
	# kafka's location, easily handle to remote kafka
	parser.add_argument('kafka_broker', help='the location of kafka broker.')

	# Parse arguments.
	args = parser.parse_args()
	symbol = args.symbol
	topic_name = args.topic_name
	kafka_broker = args.kafka_broker

	# Check if the symbol is supported
	check_symbol(symbol)

	# Intantiate a simple kafka producer.
	# https://github.com/dpkp/kafka-python
	producer = KafkaProducer(bootstrap_servers=kafka_broker)

	# Schedule and run the fetch_price function every one second
	# mark the calendar
	schedule.every(1).seconds.do(fetch_price, symbol, producer, topic_name)

	# Setup proper shutdown hook
	atexit.register(shutdown_hook, producer)

	while True:
		schedule.run_pending()

		# otherwise, schedule always check whether 1 second is reached
		# see usage part at: https://github.com/dbader/schedule
		# check calendar
		time.sleep(1)
