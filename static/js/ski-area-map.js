
// API Reference: https://github.com/mbostock/d3/wiki/API-Reference
// Awesome Tutorials on d3 / d3.geo: 
//  - http://marybecica.posterous.com/
//  - http://www.janwillemtulp.com/2011/03/20/tutorial-introduction-to-d3/
//  - http://www.recursion.org/d3-for-mere-mortals/

var mapWidth = 900;
var mapHeight = 500;
var visualizeBy = "location";

var data, areaRadiusScaler, verticalRadiusScaler,
	elevationRadiusScaler, snowfallRadiusScaler,
	trailsRadiusScaler;

	// Define the projection, d3.geo object and attach to DOM
	var projection = d3.geo.albersUsa(),
		path = d3.geo.path().projection(projection),	
		map = d3.select("#chart").append("svg")
			.attr("width", mapWidth)
			.attr("height", mapHeight);
	
	// Default scale to fit in custom width / height.
	projection.scale(950);
	
	// Draw the boundaries of the states
	var states = map.append("g").attr("id", "states");
	d3.json("static/data/us-states.json", function(json) {
		states.selectAll("path")
			.data(json.features)
			.enter().append("path")
			.attr("d", path)
			.append("svg:title")
			.text(function(d) { return d.properties.name; });
	});
	
	
	// Get the us ski areas location data	
	d3.json("get_ski_areas?usa_only=true&format=location", function(json){
		
		// Store data and setup radius scalers for each 'visualize by' perspective 
		data = json;	
		areaRadiusScaler =      d3.scale.linear().domain([data.area_min,      data.area_max]).range([2,20]);
		verticalRadiusScaler =  d3.scale.linear().domain([data.vertical_min,  data.vertical_max]).range([2,20]);
		elevationRadiusScaler = d3.scale.linear().domain([data.elevation_min, data.elevation_max]).range([2,20]);
		snowfallRadiusScaler =  d3.scale.linear().domain([data.snowfall_min,  data.snowfall_max]).range([2,20]);
		trailsRadiusScaler =    d3.scale.linear().domain([data.trails_min,    data.trails_max]).range([2,20]);
		
		$("#contentLoading").hide();
		$("#chart").fadeIn();
		
		// Render initial location points on the map
		map.selectAll("circle")
			.data(data.results)
			.enter().append("svg:circle")		
				.attr("r",   function(d) {return calculateRadius(d);})
				.attr("cx",  function(d) {return projection(d.coordinates)[0];})
				.attr("cy",  function(d) {return projection(d.coordinates)[1];})			
				.on("click", function(d) {skiAreaSelected(d);})			
				.append("title").text(function(d) {return d.name});
	});



// Calculates the radius of a ski area, given the 'visualize by' mode the app is in
function calculateRadius(skiArea) {
	if("area" === visualizeBy)
		return areaRadiusScaler(skiArea.area);
	if("vertical" === visualizeBy)
		return verticalRadiusScaler(skiArea.vertical);
	if("elevation" === visualizeBy)
		return elevationRadiusScaler(skiArea.elevation);
	if("snowfall" === visualizeBy)		
		return snowfallRadiusScaler((skiArea.snowfall > 1) ? skiArea.snowfall : 1);	 // Some ski areas don't have snowfall data...
	if("trails" === visualizeBy)
		return trailsRadiusScaler(skiArea.trails);	
	
	return 5;
}

function refresh() {
	
	visualizeBy = $('#visualizeBySelector').val();
	//states.selectAll("path").attr("d", path);
	map.selectAll("circle")		
		.attr("r",   function(d) {return calculateRadius(d);})
		.attr("cx",  function(d) {return projection(d.coordinates)[0];})
		.attr("cy",  function(d) {return projection(d.coordinates)[1];})
};

function skiAreaSelected(skiArea) {		
	$.getJSON("get_ski_areas", {id:skiArea.id, format:"long"}, function(d){
		if(d.results) {	
			populateInfoDockWithSkiArea(d.results[0]);
		}
	});          
}

$("#visualizeBySelector").removeAttr('disabled');
