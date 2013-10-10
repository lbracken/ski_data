//****************************************************************************
//*  Infodock Logic                                                          *
//****************************************************************************

function clearInfoDock() {
	$("#infoDockSection").hide();
	$("#info_name").text("");
	$("#info_location").text("");
	$("#info_area").text("");
	$("#info_vertical").text("");
	$("#info_elevation").text("");
	$("#info_base").text("");
	$("#info_snowfall").text("");
	$("#info_trails").text("");
	$("#info_lifts").text("");
}

function populateInfoDockWithSkiArea(skiArea) {
	
	clearInfoDock();
	
	// We can assume these fields are always set
	$("#info_name").text(skiArea.name);
	$("#info_location").text(
			skiArea.continent + " > " +
			skiArea.country + " > " +
			skiArea.region + " > " +
			skiArea.city);
	
	// The following fields may be unknown
	$("#info_area").text(hasPositiveValue(skiArea.area)? (formatNumber(skiArea.area) + " acres") : " Unknown");
	$("#info_vertical").text(hasPositiveValue(skiArea.vertical) ? (formatNumber(skiArea.vertical) + " ft") : " Unknown");
	$("#info_elevation").text(hasPositiveValue(skiArea.elevation) ? (formatNumber(skiArea.elevation) + " ft") : " Unknown");
	$("#info_base").text(hasPositiveValue(skiArea.baseElevation) ? (formatNumber(skiArea.baseElevation) + " ft") : " Unknown");
	$("#info_snowfall").text(hasPositiveValue(skiArea.snowfall) ? (skiArea.snowfall + "\"") : " Unknown");
	$("#info_trails").text(hasPositiveValue(skiArea.trails) ? skiArea.trails : " Unknown");
	$("#info_lifts").text(hasPositiveValue(skiArea.lifts) ? skiArea.lifts : " Unknown");
	
	var googleMapsUrl = "http://maps.google.com/maps?q="
			+ skiArea.latitude + "," + skiArea.longitude + "&num=1&t=k&z=14";
			// (num) show 1 match, (t) type is satellite, (z) zoom level 13
	
	$("#info_google_maps_link").attr("href", googleMapsUrl);
	$("#info_website_link").attr("href", skiArea.website);
	$("#info_wikipedia_link").attr("href", skiArea.wiki);

	$("#infoDockSection").show();
}



//****************************************************************************
//*  Common Util Functions                                                   *
//****************************************************************************


function hasPositiveValue(value) {	
	return (value && value > 0);	
}

// Format a number by adding commas
// From: mredkj.com/javascript/nfbasic.html
function formatNumber(nStr) {
	nStr += '';
	x = nStr.split('.');
	x1 = x[0];
	x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}