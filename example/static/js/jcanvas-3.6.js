/*!
jCanvas v3.6
Copyright 2011, Caleb Evans

Licensed under the MIT license
http://calebevans.me/projects/jcanvas/license.html
*/
(function($, document, Math, Image, undefined) {

// jCanvas function
function jC(args, defaults) {
	// Reset to defaults if nothing is passed
	if (args === undefined) {
		jC.prefs = $.extend({}, jC.defaults);
	// Merge arguments with defaults
	} else if (defaults === true) {
		jC.defaults = $.extend({}, jC.defaults, args);
		jC.prefs = $.extend({}, jC.defaults);
	// Merge arguments with preferences
	} else {
		jC.prefs = $.extend({}, jC.prefs, args);
	}
	return this;
}
// Set jCanvas default properties
jC.defaults = {
	width: 0, height: 0,
	cornerRadius: 0,
	fillStyle: 'transparent',
	strokeStyle: 'transparent',
	strokeWidth: 1,
	strokeCap: 'butt',
	strokeJoin: 'miter',
	rounded: false,
	shadowX: 0, shadowY: 0,
	shadowBlur: 3,
	shadowColor: 'transparent',
	opacity: 1,
	compositing: 'source-over',
	mask: false,
	x: 0, y: 0,
	x1: 0, y1: 0,
	x2: 0, y2: 0,
	radius: 0,
	start: 0, end: 360,
	ccw: false,
	inDegrees: true,
	fromCenter: true,
	closed: false,
	sides: 3,
	points: 5,
	angle: 0,
	text: '',
	font: 'normal 12pt sans-serif',
	align: 'center',
	baseline: 'middle',
	source: '',
	repeat: 'repeat'
};
// Merge defaults with preferences
jC.prefs = $.extend({}, jC.defaults);
jC.retro = false;

// Set global properties
jC.setGlobals = function(ctx, params) {
	ctx.fillStyle = params.fillColor || params.fillStyle;
	ctx.strokeStyle = params.strokeColor || params.strokeStyle;
	ctx.lineWidth = params.strokeWidth;
	ctx.lineCap = params.strokeCap;
	ctx.lineJoin = params.strokeJoin;
	// Set rounded corners for paths
	if (params.rounded === true) {
		ctx.lineCap = 'round';
		ctx.lineJoin = 'round';
	}
	ctx.shadowOffsetX = params.shadowX;
	ctx.shadowOffsetY = params.shadowY;
	ctx.shadowBlur = params.shadowBlur;
	ctx.shadowColor = params.shadowColor;
	ctx.globalAlpha = params.globalAlpha || params.opacity;
	ctx.globalCompositeOperation = params.compositing;
};

// Close path if chosen
jC.closePath = function(ctx, params) {
	// Mask if chosen
	if (params.mask === true) {
		ctx.save();
		ctx.clip();
	}
	if (params.closed === true) {
		ctx.closePath();
		ctx.fill();
		ctx.stroke();
	} else {
		ctx.fill();
		ctx.stroke();
		ctx.closePath();
	}
};

// Measure angles in correct units
jC.checkUnits = function(params) {
	if (params.inDegrees === true) {
		return Math.PI / 180;
	} else {
		return 1;
	}
};

// Rotate shape
jC.rotate = function(ctx, params, width, height) {
	
	// Always rotate from center
	if (params.fromCenter === false) {
		params.x += width/2;
		params.y += height/2;
	}
	params.toRad = jC.checkUnits(params);
	
	ctx.save();
	ctx.translate(params.x, params.y);
	ctx.rotate(params.angle*params.toRad);
	ctx.translate(-params.x, -params.y);
};


// Load canvas
$.fn.loadCanvas = function(ctx) {
	return this[0].getContext(ctx || '2d');
};

// Draw on canvas manually
$.fn.draw = function(callback) {
	var ctx, e;
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		callback.call(this[e], ctx);
	}
};

// Create gradient
$.fn.gradient = function(args) {
	var ctx = this.loadCanvas(),
		params = $.extend({}, jC.prefs, args),
		gradient, percent,
		stops = 0,
		i = 1;
	
	// Create radial gradient if chosen
	if (params.r1 !== undefined && params.r2 !== undefined) {
		gradient = ctx.createRadialGradient(params.x1, params.y1, params.r1, params.x2, params.y2, params.r2);
	} else {
		gradient = ctx.createLinearGradient(params.x1, params.y1, params.x2, params.y2);
	}
	
	// Count number of color stops
	while (params['c' + i] !== undefined) {
		stops += 1;
		i += 1;
	}
		
	// Calculate color stop percentages if absent
	for (i=1; i<=stops; i+=1) {
		percent = Math.round((100 / (stops-1)) * (i-1)) / 100;
		if (params['s' + i] === undefined) {
			params['s' + i] = percent;
		}
		gradient.addColorStop(params['s' + i], params['c' + i]);
	}
	return gradient;
};

// Create pattern
$.fn.pattern = function(args) {
	var ctx = this.loadCanvas(),
		params = $.extend({}, jC.prefs, args),
		img = new Image(),
		pattern;
	img.src = params.source;
	
	// Create pattern
	function create() {
		if (img.complete === true) {
			// Create pattern
			pattern = ctx.createPattern(img, params.repeat);
			return true;
		} else {
			return false;
		}
	}
	function onload() {
		create();
		// Run callback function
		if (params.load) {
			params.load.call(this[0], pattern);
		}
	}
	// Draw when image is loaded
	if (params.load) {
		img.onload = onload;
	} else {
		// Check if image is loaded
		if (create() === false) {
			img.onload = onload;
		}
	}
	return pattern;
};

// Clear canvas
$.fn.clearCanvas = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');

		jC.rotate(ctx, params, params.width, params.height);
		
		// Clear entire canvas
		if (args === undefined) {
			ctx.clearRect(0, 0, this[e].width, this[e].height);
		} else {
			ctx.clearRect(params.x-params.width/2, params.y-params.height/2, params.width, params.height);
		}
	}
	return this;
};

// Save canvas
$.fn.saveCanvas = function() {
	var ctx, e;
	
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		ctx.save();
	}
	return this;
};

// Restore canvas
$.fn.restoreCanvas = function() {
	var ctx, e;
	
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		ctx.restore();
	}
	return this;
};

// Scale canvas
$.fn.scaleCanvas = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);
		
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');

		ctx.save();
		ctx.translate(params.x, params.y);
		ctx.scale(params.width, params.height);
		ctx.translate(-params.x, -params.y);
	}
	return this;
};

// Translate canvas
$.fn.translateCanvas = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		ctx.save();
		ctx.translate(params.x, params.y);
	}
	return this;
};

// Rotate canvas
$.fn.rotateCanvas = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);
	params.toRad = jC.checkUnits(params);
	
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		ctx.save();
		ctx.translate(params.x, params.y);
		ctx.rotate(params.angle*params.toRad);
		ctx.translate(-params.x, -params.y);
	}
	return this;
};

// Draw rectangle
$.fn.drawRect = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		x1, y1, x2, y2, r;

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
		jC.rotate(ctx, params, params.width, params.height);
			
		// Draw rounded rectangle if chosen
		if (params.cornerRadius > 0) {
			x1 = params.x - params.width/2;
			y1 = params.y - params.height/2;
			x2 = params.x + params.width/2;
			y2 = params.y + params.height/2;
			r = params.cornerRadius;
			// Prevent over-rounded corners
			if ((x2 - x1) - (2 * r) < 0) {
				r = (x2 - x1) / 2;
			}
			if ((y2 - y1) - (2 * r) < 0) {
				r = (y2 - y1) / 2;
			}
			ctx.beginPath();
			ctx.moveTo(x1+r,y1);
			ctx.lineTo(x2-r,y1);
			ctx.arc(x2-r, y1+r, r, 3*Math.PI/2, Math.PI*2, false);
			ctx.lineTo(x2,y2-r);
			ctx.arc(x2-r, y2-r, r, 0, Math.PI/2, false);
			ctx.lineTo(x1+r,y2);
			ctx.arc(x1+r, y2-r, r, Math.PI/2, Math.PI, false);
			ctx.lineTo(x1,y1+r);
			ctx.arc(x1+r, y1+r, r, Math.PI, 3*Math.PI/2, false);
			ctx.fill();
			ctx.stroke();
			ctx.closePath();
		} else {
			ctx.beginPath();
			ctx.rect(params.x-params.width/2, params.y-params.height/2, params.width, params.height);
			ctx.restore();
			jC.closePath(ctx, params);
		}
	}
	return this;
};

// Draw arc
$.fn.drawArc = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);
	
	// Change default end angle to radians if needed
	if (params.inDegrees === false && params.end === 360) {
		params.end = Math.PI * 2;
	}
		
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
		jC.rotate(ctx, params, params.radius, params.radius);
		
		// Draw arc
		ctx.beginPath();
		ctx.arc(params.x, params.y, params.radius, (params.start*params.toRad)-(Math.PI/2), (params.end*params.toRad)-(Math.PI/2), params.ccw);
		// Close path if chosen
		ctx.restore();
		jC.closePath(ctx, params);
	}
	return this;
};

// Draw ellipse
$.fn.drawEllipse = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		controlW = params.width * (4/3);
		
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
		jC.rotate(ctx, params, params.width, params.height);
		
		// Create ellipse
		ctx.beginPath();
		ctx.moveTo(params.x, params.y-params.height/2);
		// Left side
		ctx.bezierCurveTo(params.x-controlW/2,params.y-params.height/2,
			params.x-controlW/2,params.y+params.height/2,
			params.x,params.y+params.height/2);
		// Right side
		ctx.bezierCurveTo(params.x+controlW/2,params.y+params.height/2,
			params.x+controlW/2,params.y-params.height/2,
			params.x,params.y-params.height/2);
		ctx.restore();
		jC.closePath(ctx, params);
	}
	return this;
};

// Draw line
$.fn.drawLine = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		l = 2, lx = 0, ly = 0;

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
		
		// Draw each point
		ctx.beginPath();
		ctx.moveTo(params.x1, params.y1);
		while (1) {
			lx = params['x' + l];
			ly = params['y' + l];
			if (lx !== undefined && ly !== undefined) {
				ctx.lineTo(lx, ly);
			} else {
				break;
			}
			l += 1;
		}
		// Close path if chosen
		jC.closePath(ctx, params);
	}
	return this;
};

// Draw quadratic curve
$.fn.drawQuad = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		l = 2,
		lx = 0, ly = 0,
		lcx = 0, lcy = 0;

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
			
		// Draw each point
		ctx.beginPath();
		ctx.moveTo(params.x1, params.y1);
		while (1) {
			lx = params['x' + l];
			ly = params['y' + l];
			lcx = params['cx' + (l-1)];
			lcy = params['cy' + (l-1)];
			if (lx !== undefined && ly !== undefined && lcx !== undefined && lcy !== undefined) {
				ctx.quadraticCurveTo(lcx, lcy, lx, ly);
			} else {
				break;
			}
			l += 1;
		}
		// Close path if chosen
		jC.closePath(ctx, params);
	}
	return this;
};

// Draw Bezier curve
$.fn.drawBezier = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		l = 2, lc = 1,
		lx = 0, ly = 0,
		lcx1 = 0, lcy1 = 0,
		lcx2 = 0, lcy2 = 0;

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
	
		// Draw each point
		ctx.beginPath();
		ctx.moveTo(params.x1, params.y1);
		while (1) {
			lx = params['x' + l];
			ly = params['y' + l];
			lcx1 = params['cx' + lc];
			lcy1 = params['cy' + lc];
			lcx2 = params['cx' + (lc+1)];
			lcy2 = params['cy' + (lc+1)];
			if (lx !== undefined && ly !== undefined && lcx1 !== undefined && lcy1 !== undefined && lcx2 !== undefined && lcy2 !== undefined) {
				ctx.bezierCurveTo(lcx1, lcy1, lcx2, lcy2, lx, ly);
			} else {
				break;
			}
			l += 1;
			lc += 2;
		}
		// Close path if chosen
		jC.closePath(ctx, params);
	}
	return this;
};

// Draw text
$.fn.drawText = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args);

	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
	
		// Set text-specific properties
		ctx.textBaseline = params.baseline;
		ctx.textAlign = params.align;
		ctx.font = params.font;
		
		ctx.strokeText(params.text, params.x, params.y);
		ctx.fillText(params.text, params.x, params.y);
		ctx.restore();
	}
	return this;
};

// Draw image
$.fn.drawImage = function(args) {
	var ctx, elem,  e,
		params = $.extend({}, jC.prefs, args),
		// Define image source
		img = new Image(),
		scaleFac;
	img.src = params.source;

	// Draw image function
	function draw(ctx) {
		if (img.complete === true) {
			scaleFac = img.width / img.height;
			// If width/height are specified
			if (params.width && params.height) {
				img.width = params.width;
				img.height = params.height;
			// If width is specified
			} else if (params.width && !params.height) {
				img.width = params.width;
				img.height = img.width / scaleFac;
			// If height is specified
			} else if (!params.width && params.height) {
				img.height = params.height;
				img.width = img.height * scaleFac;
			}						
			// Draw image
			jC.rotate(ctx, params, img.width, img.height);
			ctx.drawImage(img, params.x-img.width/2, params.y-img.height/2, img.width, img.height);
			ctx.restore();
			return true;
		} else {
			return false;
		}
	}
	// On load function
	function onload() {
		draw(ctx);
		// Run callback function
		if (params.load) {
			params.load.call(elem);
		}
	}
	// Draw image if already loaded
	for (e=0; e<this.length; e+=1) {
		elem = this[e];
		ctx = elem.getContext('2d');
		jC.setGlobals(ctx, params);
		
		// Draw when image is loaded
		if (params.load) {
			img.onload = onload;
		} else {
			// Check if image is loaded
			if (draw(ctx) === false) {
				img.onload = onload;
			}
		}
	}
	return this;
};

// Draw polygon
$.fn.drawPolygon = function(args) {
	var ctx, e,
		params = $.extend({}, jC.prefs, args),
		inner = Math.PI / params.sides,
		theta = (Math.PI/2) + inner,
		dtheta = (Math.PI*2) / params.sides,
		x1, y1, x2, y2, i;

	params.apothem = Math.cos(dtheta/2) * params.radius;
	params.closed = true;
	
	if (params.sides >= 3) {
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		jC.setGlobals(ctx, params);
		
		// Calculate points and draw
		jC.rotate(ctx, params, params.radius, params.radius);
		ctx.beginPath();
		for (i=0; i<params.sides; i+=1) {
			x1 = Math.round(params.x + (params.radius * Math.cos(theta)));
			y1 = Math.round(params.y + (params.radius * Math.sin(theta)));
			x2 = Math.round(params.y + ((params.apothem+params.apothem*params.projection) * Math.cos(theta+inner)));
			y2 = Math.round(params.y + ((params.apothem+params.apothem*params.projection) * Math.sin(theta+inner)));
			// Draw path
			if (i === 0) {
				ctx.moveTo(x1, y1);
			} else {
				ctx.lineTo(x1, y1);
			}
			// Project if chosen
			if (params.projection !== undefined) {
				ctx.lineTo(x2, y2);
			}
			theta += dtheta;
		}
		ctx.restore();
		jC.closePath(ctx, params);
	}
	}
	return this;
};

// Get pixels on the canvas
$.fn.setPixels = function(args) {
	var ctx, elem, e, i,
		params = $.extend({}, jC.prefs, args),
		imgData, data, len, px;
	
	for (e=0; e<this.length; e+=1) {
			elem = this[e];
			ctx = elem.getContext('2d');
			if (!params.x && !params.y && !params.width && !params.height) {
				params.width = elem.width;
				params.height = elem.height;
				params.x = params.width/2;
				params.y = params.height/2;
			}
			jC.rotate(ctx, params, params.width, params.height);
			imgData = ctx.getImageData(params.x-params.width/2, params.y-params.height/2, params.width, params.height);
			data = imgData.data;
			len = data.length;
			px = [];
			
			// Loop through pixels with "each" method
			if (params.each !== undefined) {
				for (i=0; i<len; i+=4) {
					px = params.each.call(elem, data[i], data[i+1], data[i+2], data[i+3]);
					data[i] = px[0];
					data[i+1] = px[1];
					data[i+2] = px[2];
					data[i+3] = px[3];
				}
			}
			// Put pixels on canvas
			ctx.putImageData(imgData, params.x-params.width/2, params.y-params.height/2);
			ctx.restore();
	}
	return this;
};

// Create jCanvas queue
jC.layers = [];

// Create layer
jC.addLayer = function(args) {
	var params = $.extend({}, jC.prefs, args);
	jC.layers.push(params);
	return params;
};

// Draw jCanvas layers
$.fn.drawLayers = function(clear) {
	var ctx, items = jC.layers.length,
		params, e, i;
	for (e=0; e<this.length; e+=1) {
		ctx = this[e].getContext('2d');
		// Optionally clear canvas
		if (clear === true) {
			ctx.clearRect(0, 0, this[e].width, this[e].height);
		}
		// Draw items on queue
		for (i=0; i<items; i+=1) {
			params = jC.layers[i];
			if (params.fn) {
				$.fn[params.fn].call(this.eq(e), params);
			}
		}
	}
	return this;
};

// Normalize layerX/layerY for jQuery mouse events
var fix = $.event.fix;
$.event.fix = function(event) {
	event = fix.call($.event, event);
	// Use offsetX/offsetY for Opera
	if (event.layerX === undefined && event.layerY === undefined) {
		event.layerX = event.offsetX;
		event.layerY = event.offsetY;
	}
	return event;
};

// Enable backward compatibility
jC.retrofit = function() {
	jC.retro = true;
	$.fn.drawQuadCurve = $.fn.drawQuad;
	$.fn.drawBezierCurve = $.fn.drawBezier;
	$.fn.canvasDefaults = jC;
	$.fn.canvas = jC;
	jC.queue = jC.layers;
	jC.create = jC.addLayer;
	$.fn.drawQueue = $.fn.drawLayers;
	return $;
};

return ($.jCanvas = jC);
}(jQuery, document, Math, Image));