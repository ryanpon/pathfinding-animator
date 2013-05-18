
/*

Goals:
-Allow visualization of graph flood
-Allow plotting of a path

*/

var CHANGE_PRED = 0
var CONSIDER = 1
var map;

function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng(37.774,-122.420),
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  test();
}

function createLL(p) {
  return new google.maps.LatLng(p[0], p[1]);
}

function test() {
  // load the sequence
  httpGet("http://localhost:5000/static/seq.j");
}

function doAnimation(data) {
  var sequence = data[0];
  var nodeCoords = data[1];
  setMarkers(sequence, nodeCoords);
  var predList = {}
  var wait = 0;
  for (var i = 0; i < sequence.length; ++i) {
    var node = sequence[i][0], actions = sequence[i][1];
    for (var k = 0; k < actions.length; ++k) {
      var edge = actions[k][0], action = actions[k][1];
      drawAnimation(node, edge, action, nodeCoords, predList, wait);
      wait += 10;
    }
  }
}

function drawAnimation(node, edge, action, nodeCoords, predList, wait) {
  if (action == CHANGE_PRED) {
    if (edge in predList) {
      predList[edge].setMap(null);  
    }
    var path = [createLL(nodeCoords[node]), createLL(nodeCoords[edge])];
    var pLine = createPolyline(path);
    predList[edge] = pLine;
    setTimeout(function() {
      pLine.setMap(map);
    }, wait);
  } else {
    // meh meh
  }
}

function setMarkers(seq, coords) {
  if (seq.length >= 2) {
    start = seq[0][0]
    end = seq[seq.length - 1][0]
    var s = new google.maps.Marker({
      position: createLL(coords[start]),
      map: map,
      title:"Start"
    });
    var e = new google.maps.Marker({
      position: createLL(coords[end]),
      map: map,
      title:"End"
    });
  }
}

function httpGet(url)
{
  $.getJSON(url, null, doAnimation);
}

function createPolyline(path) {
  pLine = new google.maps.Polyline({
    path: path,
    strokeColor: "#FF0000",
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