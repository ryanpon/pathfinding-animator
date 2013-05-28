
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
var polylines = [];
var map;

function initialize() {
  initButtons();
}

function initButtons() {
  // button group controlling algorithm selection
  $(".algo .btn").click(function() {
    $(".algo .btn").popover("hide");
    $(".algo .btn").removeClass("active");
    $(this).addClass("active");
    $(this).popover("show");
  });
  $(".algo .btn").popover({
    title: "A fuzzy algorithm!",
    placement: "top",
    content: "It's so fuzzy I'm gonna die!!!"
  });
  $("astar").data("original-title", "FUZZY!");

  $(".bidirection .btn").click(function() {
    if ($(this).hasClass("active")) {
      $(this).removeClass("btn-success");
      $(this).addClass("btn-danger");
      $(this).text("Bidirectional OFF");
    } else {
      $(this).removeClass("btn-danger");
      $(this).addClass("btn-success");
      $(this).text("Bidirectional ON");
    }
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
  setMarkerEvents();
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

function requestSequence() {
  // load the sequence
  var url = "http://localhost:5000/animation";
  //var url = "http://ryanpon.com/animation";
  var source = sMarker.getPosition();
  var dest = eMarker.getPosition();
  var bidirectional = $(".bidirection .btn").hasClass("active");
  var data = {
    "type": $(".btn-group .active").data("value"),
    "source": source.lat() + ',' + source.lng(),
    "dest": dest.lat() + ',' + dest.lng(),
    "bidirectional": bidirectional
  };
  data = encodeQueryData(data);
  $.getJSON(url, data, function(d) { doAnimation(d) } );
}

function doAnimation(data) {
  resetMapLines();
  var sequence = data["sequence"];
  var nodeCoords = data["coords"];
  var path = data["path"];
  var wait = 0;
  for (var i = 0; i < sequence.length; ++i) {
    var node = sequence[i][0], actions = sequence[i][1];
    for (var k = 0; k < actions.length; ++k) {
      var edge = actions[k];
      drawAnimation(node, edge, nodeCoords, wait);
      wait += 5;
    }
  }
  drawPath(path, wait);
}

function drawAnimation(node, edge, nodeCoords, wait) {
  var path = [createLL(nodeCoords[node]), createLL(nodeCoords[edge])];
  var pLine = createPolyline(path, "#FF0000", 1, false);
  pLine.setMap(map);
  polylines.push(pLine);
  setTimeout(function() {
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

function drawPath(path, wait) {
  var googleLLPath = [];
  for (var i = 0; i < path.length; ++i) {
    googleLLPath.push(createLL(path[i]));
  }
  shortPath = createPolyline(googleLLPath, "#000000", 2, false);
  shortPath.setMap(map);
  setTimeout(function() {
    shortPath.setVisible(true);
  }, wait);
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

function setMarkerEvents() {
  google.maps.event.addListener(sMarker, 'dragend', function() {
    requestSequence();
  });
  google.maps.event.addListener(eMarker, 'dragend', function() {
    requestSequence();
  });
}

function resetMapLines() {
  for (var i = 0; i < polylines.length; ++i) {
    polylines[i].setMap(null);
  }
  polylines = [];
  predList = {};
  if (shortPath) {
    shortPath.setMap(null);
  }
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

/*function testMarkers() {
  var markers = [];
  for (var i = 0; i < POINTS.length; ++i) {
    var m = new google.maps.Marker({
      position: createLL(POINTS[i]),
      map: map,
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