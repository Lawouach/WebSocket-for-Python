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
	
	var pos = {x: 0, y: 0};
	var accel = {x: 0, y: 0};

	me.connect = function() {
	    ws = new WebSocket(options.url+'/ws/?board_id='+board_id+"&participant_id="+participant_id);
	    ws.onopen = function(e) {};
	    ws.onclose = function(e) {
		alert("Connection lost: " + e.reason);
	    };
	    ws.onmessage = function(e) {
		if (e.data == 'clear') {
		    me.stop_motion();
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
		fillStyle: '#fff',		x: 30, y: 20,
		fontSize: 14,
		fontFamily: 'Verdana, sans-serif',
		text: 'Clear',
		click: function(layer) {
		    me.stop_motion();
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

	me.motion = function(e) {
	    var target = $(e.target);
	    if (e.type == "devicemotion") {
		accel.x = accel.x * 0.9 + e.accelerationIncludingGravity.x * 1.5;
		accel.y = accel.y * 0.9 + e.accelerationIncludingGravity.z * 1.5;
		
		if ((pos.x < 0) || (pos.x > arena.width())) {
		    accel.x = -accel.x;
		}
		if ((pos.y < 0) || (pos.y > arena.height())) {
		    accel.y = -accel.y;
		}
		
		pos.x = pos.x + accel.x;
		pos.y = pos.y - accel.y;
	    } else if (e.type == "mousemove") {
		var offset = target.offset();
		pos.x = e.clientX - offset.left;
		pos.y = e.clientY - offset.top;
	    } else if (e.type == "mousedown") {
		var offset = target.offset();
		pos.x = e.clientX - offset.left;
		pos.y = e.clientY - offset.top;
	    }
	    
	    if ((pos.x > 0) && (pos.y > 0)) {
		me.send_state(pos.x, pos.y, color);
		me.draw(pos.x, pos.y);
	    }

	    e.preventDefault();
	    e.stopPropagation();
	};

	me.stop_motion = function() {
	    if (me.ismobile()) {
		window.removeEventListener('devicemotion', me.motion, true);
	    }
	}

	me.ismobile = function() {
	    // cheap way to decide if we're mobile
	    // not bullet proof but this is a demo
	    return (Modernizr.touch == true) && window.DeviceMotionEvent;
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
	      me.motion(e);

	      if (me.ismobile()) {
		  me.stop_motion();  // just in case

		  // this is a bitch. Neither 'mouseup' nor 'touchend'
		  // are dispatched when the user release his finger
		  // from pressing on the screen. So, once started, this
		  // event will continue. sigh.
		  // Press on the "clear" button to stop that event.
		  window.addEventListener('devicemotion', me.motion, true);
	      } else {
		  board.mousemove(me.motion);
              }
	  });

	  board.mouseup(function(e) {
	      board.unbind('mousemove');
	      me.stop_motion();
          });
	};

	me.init();
    };
}(jQuery));
