
/*
Goals:

-SLIDER for speed
*/

var CENTER = [37.787403,-122.415916];            // map center
var DEFAULT_DEST = [37.788047,-122.425339];      // default routing end
var DEFAULT_SOURCE = [37.785775,-122.40602];     // default routing start
var eMarker;           // the marker indicating where routing will start
var sMarker;           // the marker indicating where routing will end
var bestPath;          // a polyline indicating the shortest path found
var predList = {};     // 
var polylines = [];    // a list of all polylines created; used for clearing map
var map;               // google maps API map
var drawSpeeds = {     // duration between rendering each segment in the graph search
    "fast": 5,
    "slow": 15,
    "instant": 0
}

function initialize() {
    initButtons();
    initHelp();

    $(window).resize(function () {
        var h = $(window).height();
        h = Math.max(h, 600)
        $("#map-canvas").css("height", (h));
        $("#buttons").css("height", (h - 9));


        var w = $(window).width();
        var a = $(".container").width();
        $("#map-canvas").css("width", (w - a - 8));
    }).resize();

    setTimeout(function () {
        $(".alert").close();
    }, 10000);
}

function initHelp() {
    $(".algo-help").click(function () {
        $(".option-help").popover("hide");
        $(".heur-help").popover("hide");
        $(this).popover("toggle");
    });
    $(".option-help").click(function () {
        $(".algo-help").popover("hide");
        $(".heur-help").popover("hide");
        $(this).popover("toggle");
    });
    $(".heur-help").click(function () {
        $(".option-help").popover("hide");
        $(".algo-help").popover("hide");
        $(this).popover("toggle");
    });

    var algoText = "Choose between three algorithms:<br>\
                    -A* search algorithm  <br>\
                    -Dijkstra's algorithm <br>\
                    -ALT: A* Landmark Triangle Inequality";
    $(".algo-help").popover({
        content: algoText,
        html: "right",
        trigger: "manual"
    });

    var optionText = "The 'Bidirectional' toggle controls whether or not the search is   \
                      performed from both the origin and destination simultaneously.     \
                      <br><br> \
                      Heuristic weight multiplies the A* and ALT heuristics by a constant\
                      factor, epsilon. Although this will cause routing to scan fewer    \
                      vertices, the path found will by at most (optimal path len) * epsilon.";
    $(".option-help").popover({
        content: optionText,
        html: "right",
        trigger: "manual"
    });

    var heurText = "Choose between three heuristics:<br>\
                    -Euclidean: straight line distance <br>\
                    -Manhattan: 'Taxicab' distance <br>\
                    -Octile: Manhattan w/ diagonal movement";
    $(".heur-help").popover({
        content: heurText,
        html: "right",
        trigger: "manual"
    });
}

function initButtons() {
    // bidirectional toggle button
    $(".bidirection .btn").click(function () {
        toggleBidirectional($(this));
    });

    $(".go .btn").click(function () {
        startAnimation();
    })
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
}

function startAnimation() {
    // load the sequence
    var url = "/animation";
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
        icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        position: createGLL(source),
        map: map,
        title:"Start",
        draggable: true
    });
    eMarker = new google.maps.Marker({
        icon: "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
        position: createGLL(dest),
        map: map,
        title:"End",
        draggable: true
    });
}

function customMarkerIcon(color) {
    var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));
    return pinImage
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

function createGLL(p) {
    return new google.maps.LatLng(p[0], p[1]);
}

function encodeQueryData(data) {
    var ret = [];
    for (var d in data)
            ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
    return ret.join("&");
}

google.maps.event.addDomListener(window, "load", initializeMap);

$(document).ready(function () {
    initialize();
});