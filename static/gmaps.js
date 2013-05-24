
/*
Goals:
--buttons! options for:
  -animation speed
  -algorithm type
    -different options for different algos
*/

var DEFAULT_SOURCE = [37.785775,-122.40602];
var DEFAULT_DEST = [37.773021,-122.445931];
var sMarker;
var eMarker;
var shortPath;
var predList = {};

function initialize() {
  $(".algo .btn").click(function() {
    $(".algo .btn").removeClass("active");
    $(this).addClass("active");
  });
}

function initializeMap() {
  // enable bootstrap buttons
  var mapOptions = {
    center: new google.maps.LatLng(37.774,-122.420),
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    disableDefaultUI: true
  };
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  setMarkers(DEFAULT_SOURCE, DEFAULT_DEST);
  setMarkerEvents(map);
}

function createLL(p) {
  return new google.maps.LatLng(p[0], p[1]);
}

function encodeQueryData(data) {
   var ret = [];
   for (var d in data)
      ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
   return ret.join("&");
}

function requestSequence(map) {
  // load the sequence
  var url = "http://localhost:5000/animation";
  //var url = "http://ryanpon.com/animation";
  var source = sMarker.getPosition();
  var dest = eMarker.getPosition();
  var algo = $(".algo .active").data("value");
  console.log(algo);
  var data = {
    "type": algo,
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
  var path = data["path"];
  drawPath(path, map);
  var wait = 0;
  for (var i = 0; i < sequence.length; ++i) {
    var node = sequence[i][0], actions = sequence[i][1];
    for (var k = 0; k < actions.length; ++k) {
      var edge = actions[k];
      drawAnimation(node, edge, nodeCoords, wait);
      wait += 0;
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
    var pLine = createPolyline(path, "#FF0000", 1);
    predList[edge] = pLine;
    pLine.setMap(map);
  }, wait);
}

function drawPath(path, map) {
  var googleLLPath = [];
  for (var i = 0; i < path.length; ++i) {
    googleLLPath.push(createLL(path[i]));
  }
  shortPath = createPolyline(googleLLPath, "#000000", 2);
  shortPath.setMap(map);
}

function setMarkers(source, dest) {
  sMarker = new google.maps.Marker({
    position: createLL(source),
    map: map,
    title:"Start",
    draggable: true
  });
  eMarker = new google.maps.Marker({
    position: createLL(dest),
    map: map,
    title:"End",
    draggable: true
  });
}

function setMarkerEvents(map) {
  google.maps.event.addListener(sMarker, 'dragend', function() {
    requestSequence(map);
  });
  google.maps.event.addListener(eMarker, 'dragend', function() {
    requestSequence(map);
  });
}

function resetMapLines() {
  for (var line in predList) {
    predList[line].setMap(null);
  }
  predList = {};
  if (shortPath) {
    shortPath.setMap(null);
  }

}

function createPolyline(path, color, size) {
  pLine = new google.maps.Polyline({
    path: path,
    strokeColor: color,
    strokeOpacity: .7,
    strokeWeight: size 
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

/*function testMarkers(map) {
  var markers = [];
  for (var i = 0; i < POINTS.length; ++i) {
    var m = new google.maps.Marker({
      position: createLL(POINTS[i]),
      map: map,
      title:"Start",
      draggable: true
    });
    markers.push(m);
  };
  return markers;
}*/

google.maps.event.addDomListener(window, 'load', initializeMap);

$(document).ready(function(){
  initialize();
});