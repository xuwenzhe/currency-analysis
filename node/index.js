var argv = require('minimist')(process.argv.slice(2)); // node index.js arg1 arg2
var port = argv['port'];
var redis_host = argv['redis_host'];
var redis_port = argv['redis_port'];
var redis_channel = argv['redis_channel'];

// Setup dependency instances. import...
var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);

// Setup redis client.
// https://github.com/NodeRedis/node_redis
var redis = require('redis');
console.log('Creating a redis client.');
var redisClient = redis.createClient(redis_port, redis_host);
console.log('Subscribe to redis channel: %s', redis_channel);
redisClient.subscribe(redis_channel);

redisClient.on('message', function(channel, message) {
	if (channel == redis_channel) {
		console.log('Message received %s', message);
		// send msg to socket.io
		io.sockets.emit('data', message);
	}
});

// Setup webapp routing. At the begining, a html file which 
// refs to all js scripts is sent to the user
// web pack manually
app.use(express.static(__dirname + '/public'));
app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist/'));
app.use('/d3', express.static(__dirname + '/node_modules/d3/'));
app.use('/nvd3', express.static(__dirname + '/node_modules/nvd3/build/'));
app.use('/bootstrap', express.static(__dirname + '/node_modules/bootstrap/dist/'));

server.listen(port, function() {
	console.log('Server started at port %d', port);
});

var shutdown_hook = function() {
	redisClient.quit();
	process.exit();
}

process.on('SIGTERM', shutdown_hook);
process.on('SIGINT', shutdown_hook);
process.on('exit', shutdown_hook);
