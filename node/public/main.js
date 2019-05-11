$(function() {
	var data_points = [];
	data_points.push({values: [], key:'BTC-USD'});
	// data_points.push({values: [], key:'LTC-USD'});

	$('#chart').height($(window).height() - $('#header').height() * 2);

    var chart = nv.models.lineChart()
        .interpolate('monotone')
        .margin({
            bottom: 100
        })
        .useInteractiveGuideline(true)
        .showLegend(true)
        .color(d3.scale.category10().range());

	chart.xAxis
			.axisLabel('Time')
			.tickFormat(formatDateTick);

	chart.yAxis
			.axisLabel('Price')

	nv.addGraph(loadGraph);

	function formatDateTick(time) {
		var date = new Date(time * 1000);  // takes timestamp in millis.
		console.log(date);
		return d3.time.format('%H:%M:%S')(date);
	}

	function loadGraph() {
		// location in index.html
		d3.select('#chart svg') 
        	.datum(data_points)
        	.transition()
        	.duration(5)
        	.call(chart);

        nv.utils.windowResize(chart.update)
        return chart;
	}

	function newDataCallBack(data) {
		var parsed = JSON.parse(data);
		var timestamp = parsed['Timestamp'];
		var price = parsed['Average'];
		var symbol = parsed['Symbol'];
		var point = {};
		point.x = timestamp;
		point.y = price;

		console.log(point);

		var i = getSymbolIndex(symbol, data_points);

		data_points[i].values.push(point);
		if (data_points[i].values.length > 100) {
			data_points[i].values.shift();
		}

		loadGraph();
	}

	function getSymbolIndex(symbol, data_points) {
		for (var i = 0; i < data_points.length; i++) {
			if (data_points[i].key == symbol) {
				return i;
			}
		}
		return -1;
	}

	var socket = io();

	socket.on('data', function(data) {
		newDataCallBack(data);
	});
});