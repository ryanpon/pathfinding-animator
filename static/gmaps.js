
/*

Goals:
-Allow visualization of graph flood
-Allow plotting of a path

*/

var DEFAULT_SOURCE = [37.785775,-122.40602];
var DEFAULT_DEST = [37.773021,-122.445931];
var s_marker;
var e_marker;
var predList = {};

function encodeQueryData(data) {
   var ret = [];
   for (var d in data)
      ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
   return ret.join("&");
}

function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng(37.774,-122.420),
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  setMarkers(DEFAULT_SOURCE, DEFAULT_DEST);
  setMarkerEvents(map);
}

function createLL(p) {
  return new google.maps.LatLng(p[0], p[1]);
}

function requestSequence(map) {
  // load the sequence
  //var url = "http://localhost:5000/animation";
  var url = "http://ryanpon.com/animation";
  var source = s_marker.getPosition();
  var dest = e_marker.getPosition();
  var data = {
    "type": "astar",
    "source": source.lat() + ',' + source.lng(),
    "dest": dest.lat() + ',' + dest.lng()
  };
  data = encodeQueryData(data);
  $.getJSON(url, data, function(d) { doAnimation(d, map) } );
}

function doAnimation(data, map) {
  resetMapLines();
  var sequence = data["sequence"];
  var nodeCoords = data["coords"];
  var wait = 0;
  for (var i = 0; i < sequence.length; ++i) {
    var node = sequence[i][0], actions = sequence[i][1];
    for (var k = 0; k < actions.length; ++k) {
      var edge = actions[k];
      drawAnimation(node, edge, nodeCoords, wait);
      wait += 5;
    }
  }
}

function drawAnimation(node, edge, nodeCoords, wait) {
  setTimeout(function() {
    if (edge in predList) {
      predList[edge].setMap(null);
      predList[edge] = null;
    }
    var path = [createLL(nodeCoords[node]), createLL(nodeCoords[edge])];
    var pLine = createPolyline(path, "#FF0000");
    predList[edge] = pLine;
    pLine.setMap(map);
  }, wait);
}

function setMarkers(source, dest) {
  s_marker = new google.maps.Marker({
    position: createLL(source),
    map: map,
    title:"Start",
    draggable: true
  });
  e_marker = new google.maps.Marker({
    position: createLL(dest),
    map: map,
    title:"End",
    draggable: true
  });
}

function setMarkerEvents(map) {
  google.maps.event.addListener(s_marker, 'dragend', function() {
    requestSequence(map);
  });
  google.maps.event.addListener(e_marker, 'dragend', function() {
    requestSequence(map);
  });
}

function resetMapLines() {
  for (var line in predList) {
    predList[line].setMap(null);
  }
  predList = {};
}

function createPolyline(path, color) {
  pLine = new google.maps.Polyline({
    path: path,
    strokeColor: color,
    strokeOpacity: .7,
    strokeWeight: 1 
  });
  return pLine
}

function setPolylineListener(pLine, map) {
  google.maps.event.addListener(map, 'click', function(event) {
    // MVCArray object
    var path = pLine.getPath();
    path.push(event.latLng);
    pLine.setPath(path);
  });
}

google.maps.event.addDomListener(window, 'load', initialize);