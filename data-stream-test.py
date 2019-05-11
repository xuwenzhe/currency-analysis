import json
import math

from unittest.mock import MagicMock
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

from time import sleep

data_stream_module = __import__("data-stream")

topic = 'test_topic'

# 42000 / 3 = 14000
test_input = [
    json.dumps({'Timestap': '1526900000001', 'Symbol': 'BTC-USD', 'LastTradePrice':'10000'}),
    json.dumps({'Timestap': '1526900000001', 'Symbol': 'BTC-USD', 'LastTradePrice':'12000'}),
    json.dumps({'Timestap': '1526900000001', 'Symbol': 'BTC-USD', 'LastTradePrice':'20000'}),
]


def _make_dstream_helper(sc, ssc, test_input):
	input_rdds = [sc.parallelize(test_input, 1)]
	input_stream = ssc.queueStream(input_rdds)
	return input_stream


def test_data_stream(sc, ssc, topic):
	input_stream = _make_dstream_helper(sc, ssc, test_input)
	print(input_stream)
	mock_kafka_producer = MagicMock()

	data_stream_module.process_stream(input_stream, mock_kafka_producer, topic)

	ssc.start()
	sleep(5)
	ssc.stop()

	mock_kafka_producer.send.assert_called_once() # test whether send() function has been called only once
	args, kwargs = mock_kafka_producer.send.call_args # list all arguments when calling send()
	print(kwargs)

	assert math.isclose(json.loads(kwargs['value'])['Average'], 14000.0, rel_tol=1e-10)
	print('test_data_stream passed!')



if __name__ == '__main__':
	sc = SparkContext('local[2]', 'local-testing')
	ssc = StreamingContext(sc, 1)

	test_data_stream(sc, ssc, topic)
