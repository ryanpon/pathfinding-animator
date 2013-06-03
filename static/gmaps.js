
/*
Goals:

-SLIDER for speed
*/

var CENTER = [37.787403,-122.415916];          // map center
var DEFAULT_DEST = [37.788047,-122.425339];      // default routing end
var DEFAULT_SOURCE = [37.785775,-122.40602];   // default routing start
var eMarker;           // the marker indicating where routing will start
var sMarker;           // the marker indicating where routing will end
var bestPath;          // a polyline indicating the shortest path found
var predList = {};     // 
var polylines = [];    // a list of all polylines created; used for clearing map
var map;               // google maps API map
var grid;              // grid to do graph searches on
var drawSpeeds = {     // duration between rendering each segment in the graph search
    "fast": 5,
    "slow": 15,
    "instant": 0
}

function initialize() {
    initButtons();

    $(window).resize(function () {
        var h = $(window).height();
        h = Math.max(h, 600)
        $("#map-canvas").css("height", (h));
        $("#buttons").css("height", (h - 9));

        var w = $(window).width();
        var a = $(".container").width();
        $("#map-canvas").css("width", (w - a - 8));
    }).resize();

}

function initButtons() {
    initMapButtons();
    // radio button group controlling algorithm selection

    // bidirectional toggle button
    $(".bidirection .btn").click(function () {
        toggleBidirectional($(this));
    });

    // radio buttons controlling draw speed
    $(".speed .btn").click(function () {
        $(".speed .btn").popover("hide");
        $(".speed .btn").removeClass("active");
        $(this).addClass("active");
        $(this).popover("show");
    });

    $(".go .btn").click(function () {
        startAnimation();
    })
}

function initMapButtons() {
    $(".map #grid").click(function () {
        if (!grid) {
            initializeGrid();            
        }
        $("#grid-canvas div").show();
        $("#map-canvas div").hide();
        // hide the popup
        $(".gmnoprint").next("div").css("z-index", -10);
    });

    $(".map #sf").click(function () {
        if (!map) {
            initializeMap();            
        }
        $("#map-canvas div").show();
        $("#grid-canvas div").hide();
        // hide the popup
        $(".gmnoprint").next("div").css("z-index", -10);
    });
}

function initializeMap() {
    var mapOptions = {
        center: createGLL(CENTER),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true

    };
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
    setMarkers(DEFAULT_SOURCE, DEFAULT_DEST);
    //setMarkerEvents();
}

function createGLL(p) {
    return new google.maps.LatLng(p[0], p[1]);
}

function encodeQueryData(data) {
    var ret = [];
    for (var d in data)
            ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
    return ret.join("&");
}

function startAnimation() {
    // load the sequence
    var url = "http://localhost:5000/animation";
    //var url = "http://ryanpon.com/animation";
    var source = sMarker.getPosition();
    var dest = eMarker.getPosition();
    var bidirectional = $(".bidirection .btn").hasClass("active");
    var heuristic = $("input:radio[name='heuristic-radio-btns']:checked").val();
    var data = {
        "type": $(".algo .active").data("value"),
        "source": source.lat() + "," + source.lng(),
        "dest": dest.lat() + "," + dest.lng(),
        "bidirectional": bidirectional,
        "epsilon": $("#epsilon input").val(),
        "heuristic": heuristic
    };
    data = encodeQueryData(data);
    var drawSpeed = getDrawSpeed();
    $.getJSON(url, data, function (d) { drawAnimation(d, drawSpeed) } );
}

function getDrawSpeed() {
    var speedText = $(".speed .active").data("value");
    return drawSpeeds[speedText];
}

function drawAnimation(data, drawSpeed) {
    resetMapLines();
    var sequence = data["sequence"];
    var nodeCoords = data["coords"];
    var path = data["path"];
    var wait = 0;
    for (var i = 0; i < sequence.length; ++i) {
        var node = sequence[i][0], actions = sequence[i][1];
        for (var k = 0; k < actions.length; ++k) {
            var edge = actions[k];
            drawSegment(node, edge, nodeCoords, wait);
            wait += drawSpeed;
        }
    }
    drawBestPath(path, wait);
}

function drawSegment(node, edge, nodeCoords, wait) {
    var path = [createGLL(nodeCoords[node]), createGLL(nodeCoords[edge])];
    var pLine = createPolyline(path, "#FF0000", 1, false);
    pLine.setMap(map);
    polylines.push(pLine);
    setTimeout(function ()  {
        if (pLine.getMap() != null) {
            if (edge in predList) {
                predList[edge].setMap(null);
                predList[edge] = null;
            }
                predList[edge] = pLine;
                pLine.setVisible(true);
        } 
    }, wait);
}

function drawBestPath(path, wait) {
    var googleLLPath = [];
    for (var i = 0; i < path.length; ++i) {
        googleLLPath.push(createGLL(path[i]));
    }
    bestPath = createPolyline(googleLLPath, "#000000", 2, false);
    bestPath.setMap(map);
    polylines.push(bestPath);
    setTimeout(function ()  {
        bestPath.setVisible(true);
    }, wait);
}

function setMarkers(source, dest) {
    sMarker = new google.maps.Marker({
        position: createGLL(source),
        map: map,
        title:"Start",
        draggable: true
    });
    eMarker = new google.maps.Marker({
        position: createGLL(dest),
        map: map,
        title:"End",
        draggable: true
    });
}

function setMarkerEvents() {
    google.maps.event.addListener(sMarker, "dragend", function ()  {
        startAnimation();
    });
    google.maps.event.addListener(eMarker, "dragend", function ()  {
        startAnimation();
    });
}

function resetMapLines() {
    for (var i = 0; i < polylines.length; ++i) {
        polylines[i].setMap(null);
    }
    polylines = [];
    predList = {};
}

function createPolyline(path, color, size, visible) {
    pLine = new google.maps.Polyline({
        path: path,
        strokeColor: color,
        strokeOpacity: .7,
        strokeWeight: size, 
        visible: visible
    });
    return pLine
}

function toggleBidirectional(elem) {
    if ($(elem).hasClass("active")) {
        $(elem).text("Bidirectional OFF");
    } else {
        $(elem).text("Bidirectional ON");
    }
}

/*function testMarkers() {
    var markers = [];
    for (var i = 0; i < POINTS.length; ++i) {
        var m = new google.maps.Marker({
            position: createGLL(POINTS[i]),
            map: map,
            draggable: true
        });
        markers.push(m);
    };
    return markers;
}*/

google.maps.event.addDomListener(window, "load", initializeMap);

$(document).ready(function () {
    initialize();
});