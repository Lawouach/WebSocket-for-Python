(function ($) {
    "use strict";

    $.board = function(options) {
	var board_id = options.board;
	var participant_id = options.participant;

	var me = this;
	var ws = null;
	var board = null;
	var tools = null;
	var arena = null;
	var colors = ['#ff1100', '#ffaa00', '#ffff11',
		      '#99dd00', '#22aaff', '#ff22aa'];
	var color = "#ff1100";
	
	me.connect = function() {
	    ws = new WebSocket('ws://192.168.1.13:8080/ws/?board_id='+board_id+"&participant_id="+participant_id);
	    ws.onopen = function(e) {};
	    ws.onclose = function(e) {
		alert("Connection lost: " + e.reason);
	    };
	    ws.onmessage = function(e) {
		console.log(e);
		if (e.data == 'clear') {
		    board.clearCanvas();
		} else {
		    var state = $.parseJSON(e.data);
		    color = state.c;
		    me.draw(state.x, state.y);
		}
	    };
	};

	me.connected = function() {
	    if (ws && (ws.readyState == WebSocket.OPEN)) {
		return true;
	    }

	    return false;
	};

	me.send_state = function(x, y, c) {
	    if (me.connected()) {
		ws.send('{"x": '+x+', "y": '+y+', "c": "'+c+'"}');
	    };
	};

	me.send_clear_board = function() {
	    if (me.connected()) {
		ws.send('clear');
	    };
	};

        me.resize = function() {
	    board.attr('width', arena.width()-70);
            board.attr('height', arena.height());
            board.attr('left', 70);
	};

	me.draw = function(x, y) {
	    board.drawArc({
		fillStyle: color,
		x: x,
		y: y,
		radius: 20,
	    });
	};

	me.setup = function() {
	    tools.drawRect({
		layer: true,
		fillStyle: '#000',
		strokeStyle: '#fff',
		strokeWidth: 2,
		cornerRadius: 10,
		x: 30, y: 20,
		width: 50, height: 30
	    });

	    tools.drawText({
		layer: true,
		fillStyle: '#fff',
		x: 30, y: 20,
		fontSize: 14,
		fontFamily: 'Verdana, sans-serif',
		text: 'Clear',
		click: function(layer) {
		    board.clearCanvas();
		    me.send_clear_board();
		}
	    });

	    var offsety = 0; 
	    for (var i=0; i<colors.length; i++) {
		tools.drawArc({
		    layer: true,
		    groups: ['tools'],
		    fillStyle: colors[i],
		    x: 30,
		    y: 70 + offsety,
		    radius: 20,
		    strokeStyle: '#fff',
		    strokeWidth: 2,
		    click: function(layer) {
			color = layer.fillStyle;
		    },
		});
		offsety += 50;
	    }
	};

	me.init = function() {
	  me.connect();

	  arena = $("#arena");
	  board = $("#board");
	  tools = $("#tools");
	  me.resize();

          $(window).resize(me.resize);
	    
	  me.setup();

	  board.mousedown(function(e) {
	      var offset = $(this).offset();
	      var x = e.clientX - offset.left;
	      var y = e.clientY - offset.top;
	      me.draw(x, y);
	      me.send_state(x, y, color);
	      board.mousemove(function(e) {
		  var offset = $(this).offset();
		  var x = e.clientX - offset.left;
		  var y = e.clientY - offset.top;
		  me.draw(x, y);
		  me.send_state(x, y, color);
	      });
	  });

	  board.mouseup(function(e) {
	      board.unbind('mousemove');
          });
	};

	me.init();
    };
}(jQuery));
