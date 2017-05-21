var canvas = document.getElementById("chaos_game");
var context  = canvas.getContext("2d");

var width  = window.innerWidth;
var height = window.innerHeight;

//Set canvas width and height
canvas.width  = width;
canvas.height = height;

function wavelengthToRGB(wavelength)
{   // Convert wavelength to RGB color. Approximately human eye vision.
    if((wavelength >= 400.0) && (wavelength <= 440.0)) {
        red = -1.0 * ((wavelength - 440.0) / 40.0);
        green = 0.0;
        blue = 1.0;
    }
    else if((wavelength >= 440.0) && (wavelength <= 490.0)) {
        red = 0.0;
        green = (wavelength - 440.0) / 50.0;
        blue = 1.0;
    }
    else if((wavelength >= 490.0) && (wavelength <= 510.0)) {
        red = 0.0;
        green = 1.0;
        blue = -1.0 * ((wavelength - 510.0) / 20.0);
    }
    else if((wavelength >= 510.0) && (wavelength <= 580.0)) {
        red = (wavelength - 510.0) / 70.0;
        green = 1.0;
        blue = 0.0;
    }
    else if((wavelength >= 580.0) && (wavelength <= 645.0)) {
        red = 1.0;
        green = -1.0 * ((wavelength - 645.0) / 65.0);
        blue = 0.0;
    }
    else if((wavelength >= 645.0) && (wavelength <= 700.0)) {
        red = 1.0;
        green = 0.0;
        blue = 0.0;
    }
    return 'rgb(' + Math.floor(255*red) + ',' +
                    Math.floor(255*green) + ',' +
                    Math.floor(255*blue) + ')';
}

function chaos_game(vertices, // number of vertices
                    scale,    // distance multiplier
                    width,    // screen width
                    height,   // screen height
                    inColor)  // color mode
{   // Draw fractal itself
    var w = width / 2.0;
    var h = height / 2.0;

    var rotOffset = Math.PI * (2.0/vertices - 0.5);
    var polyhedron = [];

    for (var i = 0; i < vertices; ++i)
    {
        var cx = (w / 2) * Math.cos((2.0*Math.PI*i / vertices) + rotOffset) + w;
        var cy = (h / 2) * Math.sin((2.0*Math.PI*i / vertices) + rotOffset) + h;

        polyhedron.push({x:cx, y:cy});
    }

    var vertex = 0; // starting point in zero vertex
    var rx = polyhedron[vertex].x;
    var ry = polyhedron[vertex].y;

    context.clearRect(0, 0, width, height); // Clear screen from previous drawing
    // Add text to the canvas
    context.font = "16px Arial";
    context.fillStyle = "black";
    context.fillText("Use controls <Up>,<Down>,<Left>,<Right> or <Space>",10,20)
    context.fillText("For color press <1> or <2>",10,40);
    context.fillText("Vertices: " + vertices + "; Scale: " + scale.toFixed(3),10,60);

    var iterations = 100000;
    for (i = 0; i < iterations; i++)
    {
        vertex = Math.floor(Math.random() * vertices); // randomly choose vertex
        var dx = polyhedron[vertex].x - rx; // x-distance from vertex to point
        var dy = polyhedron[vertex].y - ry; // y-distance from vertex to point
        rx += scale * dx; // new x-position of the point
        ry += scale * dy; // new y-position of the point

        if (inColor)
        {   // Set color to the image
            var dist = Math.sqrt(dx * dx + dy * dy);
            var wl = 400.0 + 300.0 * dist / h;
            context.fillStyle = wavelengthToRGB(wl);
        }

        context.fillRect(rx, ry, 1, 1); // draw a point as a rectangle
    }
}

var upper_limit = 1.6;
var lower_limit = 0.3;
var max_vertices = 12;
var min_vertices = 3;
var vertices = min_vertices;
var scale = lower_limit;
var step = 0.005;
var interval = 1; // milliseconds
var inColor = true;

var id = setInterval(frame, interval); // repeat periodically

function frame()
{   // Draw fractal with appropriate parameters
    if (scale > upper_limit && vertices > max_vertices)
    {   // Stop the cycle
        clearInterval(id);
        return;
    }
    
    if (scale > upper_limit || scale < lower_limit)
    {   // Add one more vertex to polyhedron and reverce scale alteration
        vertices++;
        step = - step;
    }
    
    scale += step;
    chaos_game(vertices, scale, width, height, inColor);
}

var is_moving = true;
document.body.onkeydown = function(e) // Keyboard management
{   // Execute after pressing spacebar
    if (e.keyCode === 32)
    {
        switch (is_moving)
        {
            case true: // Stop the cycle
                clearInterval(id);
                break;
            case false: // Continue the cycle
                id = setInterval(frame, interval);
                break;
        }
        is_moving = !is_moving;
    }

    if (e.keyCode >= 37 && e.keyCode <= 40)
    {
        clearInterval(id); // Stop the cycle
        
        switch (e.keyCode)
        {
            case 37: // left arrow
                scale -= step; // Move 1 step backward
                break;
            case 38: // up arrow
                scale += step * 10; // Move 10 steps forward
                break;
            case 39: // right arrow
                scale += step; // Move 1 step forward
                break;
            case 40: // down arrow
                scale -= step * 10; // Move 10 steps backward
                break;
        }
        
        if (scale < lower_limit || scale > upper_limit)
        {
            switch (e.keyCode)
            {
                case 37: // left arrow
                case 40: // down arrow
                    if (vertices > min_vertices) { vertices--; step = -step; } // move backward
                    break;
                case 38: // up arrow
                case 39: // right arrow
                    if (vertices < max_vertices) { vertices++; step = -step; } // move forward
                    break;
            }
        }
        if (scale < lower_limit) { scale = lower_limit; }
        if (scale > upper_limit) { scale = upper_limit; }

        chaos_game(vertices, scale, width, height, inColor); // draw canvas
    }

    if (e.keyCode === 49 || e.keyCode === 50)
    {
        switch (e.keyCode)
        {
            case 49: // "1" key
                inColor = true;
                break;
            case 50: // "2" key
                inColor = false;
                break;
        }
        chaos_game(vertices, scale, width, height, inColor); // draw canvas
    }
}

