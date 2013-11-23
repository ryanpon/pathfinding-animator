
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

/*
 * Initiate animation based on current settings
 */
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
    $.getJSON(url, data, function (d) { 
        drawAnimation(d["sequence"], d["coords"], d["path"], drawSpeed);
    });
}

function getDrawSpeed() {
    var speedText = $(".speed .active").data("value");
    return drawSpeeds[speedText];
}

/*
 * Arguments:
 *  sequence -- a list of line segments [[startLatLon] --> [endLatLon]]
 *  nodeCoords -- a dictionary of node coordinates
 *  bestPath -- the shortest path found: list of [lat, lon]
 *  drawSpeed -- the approximate wait time between drawing each segment
 */
function drawAnimation(sequence, nodeCoords, bestPath, drawSpeed) {
    resetMapLines();
    var curWait = 0;
    for (var i = 0; i < sequence.length; ++i) {
        var node = sequence[i][0], actions = sequence[i][1];
        for (var k = 0; k < actions.length; ++k) {
            var edge = actions[k];
            drawSegment(node, edge, nodeCoords, curWait);
            curWait += drawSpeed;
        }
    }
    drawBestPath(bestPath, curWait);
}

/*
 * The main drawing function for the expanding graph search.
 *
 * Arguments:
 *  node -- the ID of the node to draw to
 *  edge -- the ID of the edge to draw to
 *  nodeCoords -- a dictionary of node coordinates by ID
 *  wait -- the timeout in milliseconds before the segment appears
 */
function drawSegment(nodeID, edgeID, nodeCoords, wait) {
    var path = [createGLL(nodeCoords[nodeID]), createGLL(nodeCoords[edgeID])];
    var pLine = createPolyline(path, "#FF0000", 1, false);
    pLine.setMap(map);
    polylines.push(pLine);
    setTimeout(function ()  {
        if (pLine.getMap() != null) {
            if (edgeID in predList) {
                predList[edgeID].setMap(null);
                predList[edgeID] = null;
            }
                predList[edgeID] = pLine;
                pLine.setVisible(true);
        } 
    }, wait);
}

/*
 * Draws the shortest path found by the algorithm 
 */
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

/*
 * Draws green start and red end marker from provided [lat, lon]
 */
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
        trigger: "hover"
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
        trigger: "hover"
    });

    var heurText = "Choose between three heuristics:<br>\
                    -Euclidean: straight line distance <br>\
                    -Manhattan: 'Taxicab' distance <br>\
                    -Octile: Manhattan w/ diagonal movement";
    $(".heur-help").popover({
        content: heurText,
        html: "right",
        trigger: "hover"
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

google.maps.event.addDomListener(window, "load", initializeMap);
initialize();