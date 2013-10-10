
// Client DB
var searchInProgress = false;
var clientDB = {};
clientDB.skiAreas = {};
clientDB.order = [];

// Graph
var xWidth = 675;
var yHeight = 275;
var xCenter = xWidth / 2;
var yCenter = yHeight;
var yAxisStep = 100;
var graph = null;
var graphColors = ["#76A0C9", "#DBE7F0", "#A0BDD6", "#A5A4A6",  "#C7D2D9"];  
             //   ["#7595BF", "#7A9FBF", "#A3BFD9"];

var currSelectedSkiAreaId = null;

// ****************************************************************************
// *                                                                          *
// *  Ski Area AutoComplete                                                   *
// *                                                                          *
// ****************************************************************************

// Setup autocomplete, populate suggestion values and attached needed listeners
function setupAutocomplete(data) {	
	$("#addSkiAreaText").focus();
	$("#addSkiAreaText").autocomplete({
		minLength : 0,
		delay : 0,
		source : data.results,
		focus: onAutoCompleteFocus,
		select: onAutoCompleteSelection
	}).data("autocomplete")._renderItem = renderAutoCompleteItem;

	$("#addSkiAreaText").keydown(function(event){
		if (event.keyCode == '13') {
			requestAddSkiArea();
		}
	});
}


function onAutoCompleteFocus(event, ui) {
	
	// So we can't rely on the default focus behavior because that would place 
	// the entire Ski Area Text (name, state, country) in the search box when
	// an item is focused.  However, overriding the default allows mouse events
	// to trigger focus, and that doesn't play well with IE or FF.  If user has
	// the cursor over an item then typing is effectively disabled as focus 
	// keeps getting stolen. So check that this was triggered by a key event.
	if(0 == event.keyCode) {
		return;
	}	
	
	$("#addSkiAreaText").val(ui.item.name);
	return false;
}


function onAutoCompleteSelection(event, ui) {
	$("#addSkiAreaText").val(ui.item.name);
	$("#addSkiAreaText-id").val(ui.item.id);
	requestAddSkiArea();
	return false;
}

function renderAutoCompleteItem( ul, item ) {
	return $("<li></li>")
		.data("item.autocomplete", item )
		.append("<a><span class='addSkiAreaText-label'>" + item.name + "</span>" +
				"<span class='addSkiAreaText-desc'>" + item.desc + "</span></a>")
		.appendTo(ul);
}

function disableAddSkiArea() {
	$("#addSkiAreaText").autocomplete({disabled: true});
	$("#addSkiAreaText").autocomplete("close");
	$("#addSkiAreaText").attr("disabled", "disabled");
	$("#addSkiAreaLoading").fadeIn();
	$("#addSkiAreaMsg").text("");
	$("#addSkiAreaMsg").hide();
}

function enableAddSkiArea() {
	$("#addSkiAreaText-id").val(null);
	$("#addSkiAreaLoading").hide();
	$("#addSkiAreaText").val("");
	$("#addSkiAreaText").autocomplete({disabled: false});
	$("#addSkiAreaText").removeAttr("disabled"); 
	$("#addSkiAreaText").focus();
}


//****************************************************************************
//*                                                                          *
//*  Manage Client-side Ski Area DB                                          *
//*                                                                          *
//****************************************************************************

// To Handle:
//  - User types name, then hits enter (be sure to trim)
//  + User keyboards to a suggestion
//  + User clicks a suggestion
//  + User clicks the search button
function requestAddSkiArea() {
	
	// Prevent multiple searches
	if(searchInProgress) {
		return; 
	}
	
	searchInProgress = true;    
	disableAddSkiArea();    
	          
	// First check if the user selected an autocomplete suggestion.
	// If so we have a SkiArea Id, use that.
	var skiAreaId = $("#addSkiAreaText-id").val();        
	if(skiAreaId) {
		$.getJSON("get_ski_areas", {id:skiAreaId, format:"full"}, addSkisAreas);          
		return;
	}
  
	// Search for the ski area by the name provided.        
	var skiAreaName = $("#addSkiAreaText").val();
	if(skiAreaName) {
		// Server-side will only return results if there was a single match
		$.getJSON("get_ski_areas", {name:skiAreaName, format:"full"}, addSkisAreas);
		return;
	}
	
	// No search actually took place....
	enableAddSkiArea();
	searchInProgress = false;
}

function addSkisAreas(data) {

	var skiAreaAdded = false;	
	if(data.results) {
		$.each(data.results, function() {
			var skiAreaId = currSelectedSkiAreaId = this.id;		
			
			// Make sure we don't add the ski area twice
			if(!clientDB.skiAreas[skiAreaId]) {
				skiAreaAdded = true;
				clientDB.skiAreas[skiAreaId] = this;			
				clientDB.order.push({id:skiAreaId, vertical:this.vertical});
			}
		});
		
		// After all items have been added, sort the order array.  There are
		// better ways to handle this (linklist), but this is quick and easy
		// so it'll work for now with the smaller clientDB data sizes.
		if(skiAreaAdded) {
			clientDB.order.sort(function(a,b){
				return b.vertical - a.vertical;
			});
		}	
	} else {
		// TODO: An error message here could be helpful...
		return;
	}
	
	if(data.msgs) {
		$("#addSkiAreaMsg").text(data.msgs);
		$("#addSkiAreaMsg").fadeIn();
	}	

	enableAddSkiArea();
	searchInProgress = false;
	
	renderSkiAreaList();
	renderSkiAreaGraph();
	populateInfoDock();
}

function removeSkiArea(skiAreaId) {
	removeSkiAreas([skiAreaId]);
}

function removeSkiAreas(skiAreaIds) {
	
	if(skiAreaIds) {
		$.each(skiAreaIds, function() {			
			var toRemove = clientDB.skiAreas[this];
			
			// Remove SkiArea from clientDB skiAreas map, and order array
			delete clientDB.skiAreas[toRemove.id];
			clientDB.order = jQuery.grep(clientDB.order, function (i) {
				return i.id != toRemove.id;
			});			
			
			// If item to remove is the selected item, then clear infodock
			if(currSelectedSkiAreaId == toRemove.id) {
				currSelectedSkiAreaId = null;
				clearInfoDock();
			}			
		});
	}
	
	if(null === currSelectedSkiAreaId && clientDB.order.length > 0) {
		currSelectedSkiAreaId = clientDB.order[0].id;
	}
	
	renderSkiAreaList();
	renderSkiAreaGraph();
	populateInfoDock();
}

function removeAllSkiAreas() {

	clientDB.skiAreas = {};
	clientDB.order = [];
	currSelectedSkiAreaId = null;
	
	removeSkiAreas(null);
}

function isClientDBEmpty() {
	return (clientDB.order.length < 1);
}


//****************************************************************************
//*                                                                          *
//*  Ski Area Graph Logic                                                    *
//*                                                                          *
//****************************************************************************

function renderSkiAreaGraph() {
	
	// Hide and clear the graph
	if(graph) {
		graph.clear();
	} else {
		graph = Raphael("skiAreaGraphSection", xWidth, yHeight); 
	}
	$("#skiAreaGraphSection").hide();
	
	// Nothing to render if clientDB is empty
	if(isClientDBEmpty()) {
		return;
	}
	
	var skiAreaGraphItems = [];
	var maxHeight = 0;
	var maxWidth = 0;
	
	$.each(clientDB.order, function() {
		
		var skiArea = clientDB.skiAreas[this.id];		
		//var areaSquared = 4046 * skiArea.area;	// Meters
		var areaSquared = 43560 * skiArea.area;	// Feet		
		var width = (areaSquared / 2) / (3.1459 * skiArea.vertical);
		var height = skiArea.vertical;
			
		// Record the x and y max values
		if(width > maxWidth) {
			maxWidth = width; 
		}		
		if(height > maxHeight) {
			maxHeight = height; 
		}
		
		skiAreaGraphItems.push({x:width, y:height});
	});
	
	// Determine the max range of the y-axis, and what scale is required
	var yMax = Math.floor(maxHeight / yAxisStep) * yAxisStep + yAxisStep;	
	var scale = yHeight / yMax;
	
	// Now confirm that the widest graph item also is in bounds. Remember to 
	// multiply width by two since we see the full width (but only half of 
	// the ellipse height)
	if( ((2 * maxWidth) * scale) > xWidth) {
		scale = xWidth / (2 * maxWidth);
	}	
	
	// Add each ski area to the graph, render according to order (vertical)
	var ctr = 0;
	$.each(clientDB.order, function() {		
		var w = skiAreaGraphItems[ctr].x * scale;
		var h = skiAreaGraphItems[ctr].y * scale;		
		renderSkiAreaGraphItem(this, w, h, ctr++);	
	});	
	
	// Add tick marks along the y-axis of the graph to show vertical
	var ctr = 0;
	var tickCount = 4;
	var yTop = parseInt(yHeight - (skiAreaGraphItems[0].y * scale));
	var step = parseInt((yHeight - yTop) / tickCount);
	graph.path("M0 " + (yHeight-1) + "L5 " + (yHeight-1));
	for(ctr = 0; ctr < tickCount; ctr++) {
		var y = yTop + (step * ctr);
		graph.path("M0 " + y + "L5 " + y);
	}
	
	// Mark the elevation on the top tick mark
	if(yTop < 13) { yTop = 13; }	// Stay in-bounds
	if($.browser.webkit) { yTop = yTop/2; }	// Fixes a bug/feature in WebKit that causes text to be rendered incorrectly for y value. (Chrome 16 and Safari 5.1)
	graph.text(13, yTop, formatNumber(clientDB.order[0].vertical) + " ft\nVertical").attr({'text-anchor': 'start', 'font-size':11});

	$("#contentLoading").hide();
	$("#skiAreaContent").show();
	$("#skiAreaGraphSection").fadeIn("slow");
}

function renderSkiAreaGraphItem(skiArea, width, height, ctr) {
	
	// Create and setup the graph item
	var graphItem = graph.ellipse(xCenter, yCenter, width, height);
	graphItem.id = ("skiAreaGraphItem_" + skiArea.id);
	graphItem.attr("title", skiArea.name);
	graphItem.attr("fill", graphColors[ctr % graphColors.length]);
	graphItem.attr("stroke", "#fff");
	graphItem.attr("cursor", "pointer");
	graphItem.attr("opacity", .85);
	
	// Attach shared listeners
	graphItem.hover(onHoverInSkiArea, onHoverOutSkiArea);
	graphItem.click(onClickSkiArea);
}




//****************************************************************************
//*                                                                          *
//*  Ski Area List Logic                                                     *
//*                                                                          *
//****************************************************************************

function renderSkiAreaList() {

	// Clear the ski area list
	$("#skiAreaList").hide();
	$("#skiAreaList").html("");
	
	// Nothing to render if clientDB is empty
	if(isClientDBEmpty()) {
		return;
	}
	
	// Add each ski area to the list, render according to order
	var ctr = 0;
	$.each(clientDB.order, function() {
		renderSkiAreaListItem(clientDB.skiAreas[this.id], ctr++);
	});

	$("#skiAreaList").fadeIn("slow");
}

function renderSkiAreaListItem(skiArea, ctr) {
	var skiAreaListItem = $("<div class='skiAreaListItem'></div>");
	var skiAreaListItemInner = $("<div class='skiAreaListItem-Inner'></div>");
	var skiAreaListItemClose = $("<div class='skiAreaListItem-Close'></div>");
	var skiAreaListItemCloseImg = $("<img src='static/images/icons/close.png' title='Remove'/>");
	
	skiAreaListItem.append(skiAreaListItemInner);
	skiAreaListItem.append(skiAreaListItemClose);
	skiAreaListItemClose.append(skiAreaListItemCloseImg);
		
	skiAreaListItem.attr("id", "skiAreaListItem_" + skiArea.id);	
	skiAreaListItem.hover(onHoverInSkiArea, onHoverOutSkiArea);
	skiAreaListItem.click(onClickSkiArea);
	skiAreaListItem.css("background-color", graphColors[ctr % graphColors.length]);
	
	skiAreaListItemInner.text(skiArea.name);
	skiAreaListItemInner.attr("title", skiArea.name);
	
	skiAreaListItemCloseImg.click(
			function(){removeSkiArea(skiArea.id);});
	
	skiAreaListItemCloseImg.hover(
			function(){skiAreaListItemCloseImg.attr("src", "static/images/icons/close_hover.png");},
			function(){skiAreaListItemCloseImg.attr("src", "static/images/icons/close.png");});
	
	
	
	$("#skiAreaList").append(skiAreaListItem);
}


//****************************************************************************
//*                                                                          *
//*  Ski Area Graph & List Shared Logic                                      *
//*                                                                          *
//****************************************************************************

var hoveredGraphItem = null;
var hoveredGraphItemGlow = null;
var hoveredListItem = null;

function onHoverInSkiArea() {
	
	var skiAreaId = this.id.split("_");
	if(skiAreaId.length === 2) {
		skiAreaId = skiAreaId[1];
		
		if(graph) {
			hoveredGraphItem = graph.getById("skiAreaGraphItem_" + skiAreaId);
			hoveredGraphItemGlow = hoveredGraphItem.glow();
		}
		
		hoveredListItem = $("#skiAreaListItem_" + skiAreaId);
		hoveredListItem.addClass("skiAreaListItem-hover");
	}	
}

function onHoverOutSkiArea() {
	
	if(hoveredGraphItem) {}
	
	if(hoveredGraphItemGlow) {
		hoveredGraphItemGlow.remove();
	}
	
	if(hoveredListItem) {
		hoveredListItem.removeClass("skiAreaListItem-hover");
	}
	
	hoveredGraphItem = null;
	hoveredGraphItemGlow = null;
	hoveredListItem = null;
}

function onClickSkiArea() {
	var skiAreaId = this.id.split("_");
	if(skiAreaId.length === 2) {		
		currSelectedSkiAreaId = skiAreaId[1];		
		populateInfoDock();
	}	
}

function populateInfoDock() {
	
	clearInfoDock();	
	if(null === currSelectedSkiAreaId) {
		return;
	}		
	var skiArea = clientDB.skiAreas[currSelectedSkiAreaId];
	populateInfoDockWithSkiArea(skiArea);
}

// Get the set of ski areas that should be loaded at startup
function getStartupSkiIds() {

	// Try to get any ids set in the window hash
	if(window.location.hash) {		
		var parsedHash = new Array();
		parsedHash = window.location.hash.split("=");
		if(parsedHash[0] === "#load" && parsedHash.length == 2) {
			return "[" + parsedHash[1] + "]";
		}
	} 
	// Default ids to load: Steamboat, Snowbird, Stowe and Snowshoe
	return "[1859,1163,1376,1744]";
}


//****************************************************************************
//*                                                                          *
//*  Misc                                                                    *
//*                                                                          *
//****************************************************************************

$(document).ready(function() {	
	// Setup buttons
	$("#addSkiAreaButton").button({icons: {primary:"ui-icon-search" }, text: false});
	$("#addSkiAreaButton").click(requestAddSkiArea);
	
	// Request to pre-load a set of ski areas
	$.getJSON("get_ski_areas", {id:getStartupSkiIds(), format:"full"}, addSkisAreas);
	
	// Request values for ski area autocomplete
	$.getJSON("get_ski_areas", {order:"name", format:"autocomplete"}, setupAutocomplete);
	
	// Attach handlers to show more details in welcome text
	$("#welcomeText-showMoreDetails").toggle(
		function(){
			$("#welcomeText-moreDetails").fadeIn();
			$("#welcomeText-showMoreDetails").text("<< Less Details");
		},
		function(){
			$("#welcomeText-moreDetails").hide();
			$("#welcomeText-showMoreDetails").text("More Details >>");
		}
	);
});
