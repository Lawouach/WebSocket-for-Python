
var initWebSocket = function() { 
    var ws = new WebSocket('ws://localhost:9000/ws');

    $(window).unload(function() {
	ws.close();
    });

    ws.onopen = function (evt) {
    };

    ws.onmessage = function (evt) {
	console.log(evt.data.split(' '));
	var sensors = evt.data.split(' ');
	$("#canvas").clearCanvas();
	drawAzimuth(Math.floor(parseFloat(sensors[0])));
	drawPitch(Math.floor(parseFloat(sensors[1])));
	drawRoll(Math.floor(parseFloat(sensors[2])));
	drawX(Math.abs(Math.floor(parseFloat(sensors[3]))));
	drawY(Math.abs(Math.floor(parseFloat(sensors[4]))));
	drawZ(Math.abs(Math.floor(parseFloat(sensors[5]))));
    };
};

var drawArc = function(pos, value, label) {
    $("#canvas").drawText(
	{
	    strokeStyle: "#000",
	    text: label,
	    x: pos, y: 100
	}
    );
    
    $("#canvas").drawArc(
	{
	    strokeStyle: "#F77B00",
	    strokeWidth: 15,
	    x: pos, y: 200,
	    radius: 50,
	    start: 0, end: value
	}
    );
};

var drawSegment = function(lblx, lbly, x1, x2, y1, y2, label) {
    $("#canvas").drawText(
	{
	    strokeStyle: "#000",
	    text: label,
	    x: lblx, y: lbly
	}
    );

    $("#canvas").drawLine(
	{
	    strokeStyle: "#F77B00",
	    strokeWidth: 15,
	    x1: x1, y1: y1,
	    x2: x2, y2: y2
	}
    );
};

var drawAll = function() {
    drawAzimuth(Math.floor(Math.random() * 360));
    drawPitch(Math.floor(Math.random() * 360));
    drawRoll(Math.floor(Math.random() * 360));
    drawX(Math.floor(Math.random() * 20));
    drawY(Math.floor(Math.random() * 20));
    drawZ(Math.floor(Math.random() * 20));
};

var drawAzimuth = function(azimuth) {
    var offset = 75;
    drawArc(offset, azimuth, 'azimuth');
};

var drawPitch = function(pitch) {
    drawArc(200, pitch, 'pitch');
};

var drawRoll = function(roll) {
    drawArc(350, roll, 'roll');
};

var drawX = function(x) {
    x = 650 + Math.abs(Math.floor(200 * x / 20));
    drawSegment(880, 300, 650, x, 300, 300, 'x');
};

var drawY = function(y) {
    y = 300 - Math.abs(Math.floor(170 * y / 20));
    drawSegment(650, 100, 650, 650, 300, y, 'y');
};

var drawZ = function(z) {
    var x = 650 - Math.abs(Math.floor(130 * z / 20));
    var y = 300 + Math.abs(Math.floor(100 * z / 20));
    drawSegment(500, 410, 650, x, 300, y, 'z');
};
