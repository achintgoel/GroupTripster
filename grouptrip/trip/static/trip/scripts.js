var infowindow = null;
var map = null;
var geocoder;
var activity_markers = {};
var autocomplete;
var autocomplete2;
var autocomplete3;
var autocomplete4;
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


//function that is called when start new trip button is pressed
function onCreateNewTrip(){
	//document.getElementById("createTrip").reset();
	$('#createTrip').modal();
}

//function that is called when save is pressed on the modal
function onSaveTrip(){
	// build an object of review data to submit
	var trip = { 
		name: jQuery("#id_name").val(),
		start_date: jQuery("#id_start_date").val(),
		end_date: jQuery("#id_end_date").val(),
		location: jQuery("#id_location").val() };
	// make request, process response
	jQuery.post("/trip/save/", trip,
		function(response){
			if(response.success == "True"){
				$('#createTrip').modal('hide');
				jQuery("#myTrips").prepend(response.html).slideDown();
				
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}


//function that is called when start new trip button is pressed
function onCreateNewActivity(){
	document.getElementById("createActivityForm").reset();
	$('#createActivity').modal();
}

//function that is called when save is pressed on the modal
function onFinderSearch(){
	// build an object of review data to submit
	jQuery("#finder_results").empty();
	var query = { 
		where: jQuery("#where").val(),
		type: jQuery("#type").val() };
	// make request, process response
	jQuery.post("/finder/get_finder_results/", query,
		function(response){
			if(response.success == "True"){	
				jQuery("#finder_results").append(response.html);
				jQuery(".finder-add").click(function () {
					var name = $(this).data( "name" );
					onAddActivityReal(name);
				});
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}

function onFinderYelpSearch(){
	// build an object of review data to submit
	jQuery("#finder_results").empty();
	var query = { 
		where: jQuery("#where").val(),
		term: jQuery("#what").val() };
	// make request, process response
	jQuery.get("/finder/get_finder_results_yelp/", query,
		function(response){
			if(response.success == "True"){	
				jQuery("#finder_results").append(response.html);
				jQuery(".finder-add").click(function () {
					var name = $(this).data( "name" );
					var address = $(this).data( "address" );
					onAddActivityReal(name, address);
				});
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}

//function that is called when save is pressed on the modal
function onFinderExpediaSearch(){
	// build an object of review data to submit
	jQuery("#finder_results").empty();
	var query = {
					location: jQuery("#hotel_location").val(),
					check_in: jQuery("#hotel_check_in").val(),
					check_out: jQuery("#hotel_check_out").val(),
					rooms: jQuery("#hotel_rooms").val(),
					num_adults: jQuery("#hotel_num_adults").val()
				};
	// make request, process response
	jQuery.post("/finder/get_finder_results_expedia/", query,
		function(response){
			if(response.success == "True"){	
				jQuery("#finder_results").append(response.html);
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}


function initialize() {
	  geocoder = new google.maps.Geocoder();
	  map = new google.maps.Map(document.getElementById('map-canvas'), {
	    mapTypeId: google.maps.MapTypeId.ROADMAP
	  });
	  var defaultBounds = new google.maps.LatLngBounds(
	      new google.maps.LatLng(-33.8902, 151.1759),
	      new google.maps.LatLng(-33.8474, 151.2631));
	  map.fitBounds(defaultBounds);
	
	  var input = /** @type {HTMLInputElement} */(document.getElementById('target'));
	  var searchBox = new google.maps.places.SearchBox(input); 
	  
	  var options = {
		  types: ['geocode']
		  };
	  var input2 = /** @type {HTMLInputElement} */(document.getElementById('id_address'));
	  autocomplete = new google.maps.places.Autocomplete(input2, options);
	  
	  var options2 = {
		  types: ['establishment']
		  };
	  var input3 = /** @type {HTMLInputElement} */(document.getElementById('id_name'));
	  autocomplete2 = new google.maps.places.Autocomplete(input3, options2);
	  
	  var input4 = /** @type {HTMLInputElement} */(document.getElementById('where'));
	  autocomplete3 = new google.maps.places.Autocomplete(input4, options);
	  
	  var input5 = /** @type {HTMLInputElement} */(document.getElementById('hotel_location'));
	  autocomplete4 = new google.maps.places.Autocomplete(input5, options);
	  
	  var markers = [];
	  google.maps.event.addListener(autocomplete2, 'place_changed', function() {
	  	findActivityPhotos();
	  });
	
	  google.maps.event.addListener(searchBox, 'places_changed', function() {
	    var places = searchBox.getPlaces();
	
	    for (var i = 0, marker; marker = markers[i]; i++) {
	      marker.setMap(null);
	    }
	
	    markers = [];
	    var bounds = new google.maps.LatLngBounds();
	    for (var i = 0, place; place = places[i]; i++) {
	      var image = {
	        url: place.icon,
	        size: new google.maps.Size(71, 71),
	        origin: new google.maps.Point(0, 0),
	        anchor: new google.maps.Point(17, 34),
	        scaledSize: new google.maps.Size(25, 25)
	      };
		
		  //TODO:change this so you construct the html string here, not put it in places_info_window.html
		  jQuery("#place_name").html("<p><strong>"+place.name+"</strong></p>");
		  jQuery("#placeName").val(place.name);
	 	  jQuery("#place_address").html("<p>"+place.formatted_address+"</p>");
	 	  jQuery("#placeAddress").val(place.formatted_address);
	 	  jQuery("#placeReference").val(place.reference);

	      var contentString = jQuery("#infowindow").html();
	      var marker = new google.maps.Marker({
	        map: map,
	        title: place.name,
	        position: place.geometry.location,
	        html: contentString
	      });
	    
	    
	    var infowindow = new google.maps.InfoWindow({content:"holding..."});
		
		google.maps.event.addListener(marker, 'click', function() {
			infowindow.setContent(this.html);
	  		infowindow.open(map,this);
	  		
		});
	      markers.push(marker);
	
	      bounds.extend(place.geometry.location);
	    }
	
	    map.fitBounds(bounds);
	  });
	
	  google.maps.event.addListener(map, 'bounds_changed', function() {
	    var bounds = map.getBounds();
	    searchBox.setBounds(bounds);
	  });
	  
}

function findActivityPhotos() {
	jQuery("#id_activity_photo").empty();
	  	var place = autocomplete2.getPlace();
	  	jQuery("#activity_photo_collapse").collapse('show');
	  	for (var i = 0, photo; photo = place.photos[i]; i++) {
	  		var image_url = photo.getUrl({'maxWidth': 80, 'maxHeight': 80});
	  		var img_html = '<a href="#"><img src="' + image_url +'" class="img-thumbnail"></a>';
	  		jQuery("#id_activity_photo").append(img_html);
	  	}
	  	
	  	jQuery("#id_activity_photo a").click(function(event){
			event.preventDefault();
			$('#id_activity_photo a img.activity-photo-selected').removeClass('activity-photo-selected');
    		jQuery("img", this).addClass('activity-photo-selected');
    		
		});
}

function onPlaceOnMap(name, address) {
	geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
      });
      activity_markers[name] = marker;
    } 
  });
}

function onShowOnMap(name) {
	marker = activity_markers[name];
	map.setCenter(marker.position);
	map.setZoom(18);
}

//google.maps.event.addDomListener(window, 'load', initialize);

//TODO: Replace this when you change add activity button to have unobstrusive javascript
function onAddActivity() {
	document.getElementById("createActivityForm").reset();
	jQuery("#id_name").val(jQuery("#placeName").val());
	jQuery("#id_address").val(jQuery("#placeAddress").val());
	jQuery("#id_reference").val(jQuery("#placeReference").val());
	$('#createActivity').modal();
	findActivityPhotos();
}

function onAddActivityReal(name, address) {
	document.getElementById("createActivityForm").reset();
	jQuery("#id_name").val(name);
	jQuery("#id_address").val(address);
	$('#createActivity').modal();
	findActivityPhotos();
}

function onEditActivity(activity_id, name, start_date, start_time, address, description, category) {
	document.getElementById("createActivityForm").reset();
	jQuery("#id_activity_id").val(activity_id);
	jQuery("#id_name").val(name);
	jQuery("#id_start_date").val(start_date);
	jQuery("#id_start_time").val(start_time);
	jQuery("#id_address").val(address);
	jQuery("#id_description").val(description);
	jQuery("#id_category").val(category);
	$('#createActivity').modal();
}

//function that is called when save is pressed on the modal
function onSaveActivity(){
	// build an object of review data to submit
	var activity = { 
		activity_id: jQuery("#id_activity_id").val(),
		name: jQuery("#id_name").val(),
		start_date:jQuery("#id_start_date").val(),
		start_time: jQuery("#id_start_time").val(),
		category: jQuery("#id_category").val(),
		address: jQuery("#id_address").val(),
		description: jQuery("#id_description").val(),
		photo: jQuery('#id_activity_photo a img.activity-photo-selected').attr('src'),
		reference: jQuery("#id_reference").val(),
		slug: jQuery("#id_slug").val() };
	// make request, process response
	jQuery.post("/trip/add_activity/", activity,
		function(response){
			if(response.success == "True"){
				//TODO:maintain order within that div
				jQuery("#createActivity").modal('hide');
				//TODO:add handling for case when activity is edited (change its content or move it to a different date)
				if(response.edited == "False") {
					jQuery(response.activities_div_id).prepend(response.html);
					//Discussion setup
					jQuery('.activity_summary_content').carousel({interval : false});
					jQuery(".discussion_link").click(function (e) {
						e.preventDefault();
						var activity_id = $(this).data( "activity-id" );
						var carousel_id = '#'+activity_id+'_activity_summary_content';
						jQuery(carousel_id).carousel('next');
					});
					jQuery(".comment_post").click(function () {
						var activity_id = $(this).data( "activity-id" );
						onSaveComment(activity_id);
					});
					onPlaceOnMap(name, address);
					jQuery(".show-on-map").click(function () {
						var name = $(this).data( "name" );
						onShowOnMap(name);
					});
					jQuery(response.no_activities_div_id).remove();
					jQuery(response.activities_div_id).collapse('show');
				}
				
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}


//function that is called when the page is first loaded to get activity data
function loadActivityData(){
	var data = { 
		slug: jQuery("#id_slug").val() };
	// make request, process response
	jQuery.get("/trip/get_activities/", data,
		function(response){
				for (var i = 0, activity; activity = response[i]; i++) {
					onPlaceOnMap(activity.fields.name, activity.fields.address);
					//getPlaceDetails(activity.fields.reference, activity.pk);
				}
		}, "json");
}

function getPlaceDetails(reference, id) {
	//TODO set more than just the photo	
	var request = {
  		reference: reference
	};
	
	var activities_div_id = "#my%sActivities" % id;
	var service = new google.maps.places.PlacesService(map);
	service.getDetails(request, setPlaceDetails);
	
	function setPlaceDetails(place, status) {
  		if (status == google.maps.places.PlacesServiceStatus.OK) {
  			//TODO CHANGE THIS
  			var div_id = "#ACTIVITY_IDactivityPicture";
  			div_id = div_id.replace("ACTIVITY_ID", id.toString())
  			jQuery(div_id).attr("src", place.photos[0].getUrl({'maxWidth': 80, 'maxHeight': 80}));
  		}
	}
}

function onAddTask() {
	$('#task_form_div').collapse('show');
}

function onCancelTask() {
	document.getElementById("task_form").reset();
	$('#task_form_div').collapse('hide');
}

function onSaveTask() {
	// build an object of review data to submit
	var task = { 
		name: jQuery("#task_name").val(),
		category: jQuery("#task_category").val(),
		description: jQuery("#task_description").val(),
		link: jQuery("#task_link").val(),
		slug: jQuery("#id_slug").val(),
		assign_to: jQuery("#task_assign_to").val() };
	// make request, process response
	jQuery.post("/tasks/save_task/", task,
		function(response){
			if(response.success == "True"){
				//TODO:maintain order within that div
				document.getElementById("task_form").reset();
				jQuery("#no_tasks").empty();
				jQuery("#tasks_table").prepend(response.html).slideDown();
				jQuery(".complete_task").change(function () {
					if($(this).is(':checked')) {
						onCompleteTask($(this).val());
					}
					
				});
			}
			else{
				//TODO:Add in error cases, show errors in form!
			}
		}, "json");
}

function onCompleteTask(task_id) {
	var data = { 
		task_id: task_id,
		slug: jQuery("#id_slug").val()};
		
	jQuery.post("/tasks/complete_task/", data,
		function(response){
			if(response.success == "True"){
				//$('.task_name_display').wrapInner('<div class="new" />');
			}
			else{
				//TODO:Add in error cases
			}
		}, "json");
}

function showTaskDetails(task_num) {
	jQuery('#tasks_content').carousel(task_num);
}

function onSaveComment(activity_id) {
	var comment = { 
		activity_id: activity_id,
		comment: jQuery("#"+activity_id+"_id_comment").val()};
		
	jQuery.post("/trip/save_comment/", comment,
		function(response){
			if(response.success == "True"){
				jQuery("#"+activity_id+"_no_comments").empty();
				document.getElementById(activity_id+"_comment_form").reset();
				jQuery("#"+activity_id+"_all_comments").append("<p>"+response.html+"</p>").slideDown();
			}
			else{
				//TODO:Add in error cases
			}
		}, "json");
}

$(window).resize(function () {
    var h = $(window).height(),
        offsetTop = 60; // Calculate the top offset

    jQuery("#map-canvas").css('height', (h));
    jQuery("#map-canvas").css('width', "100%");
    jQuery(".left-content").css('height', (h));
}).resize();


function itineraryInit() {}
function finderInit() {}

function tasksInit() {
	//TASKS SETUP
	jQuery("#add_task").click(onAddTask);
	jQuery("#save_task").click(onSaveTask);
	jQuery("#cancel_task").click(onCancelTask);
	jQuery(".complete_task").change(function (event) {
		event.stopPropagation();
		if($(this).is(':checked')) {
			onCompleteTask($(this).val());
		}
		//TODO: else unfinish task
		
	});
	jQuery(".complete_task").click(function (event) {
		event.stopPropagation();
	});
	jQuery('#tasks_content').carousel({interval : false});
	jQuery("#tasks_table tr").click(function () {
		var task_num = $(this).data( "task-num" );
		showTaskDetails(task_num);
	});
	jQuery(".prev_tasks").click(function () {
		jQuery('#tasks_content').carousel(0);
	});
}

function prepareDocument() {
	jQuery("#createTripButton").click(onCreateNewTrip);
	jQuery("#id_start_date").datepicker({
      showButtonPanel: true
    });
	jQuery("#id_end_date").datepicker({
      showButtonPanel: true
    });
	jQuery("#saveTripButton").click(onSaveTrip);
	jQuery("#add_activity_link").click(onCreateNewActivity);
	
	
	jQuery("#finder_search").click(onFinderYelpSearch);
	
	tasksInit();
	
	jQuery(".show-on-map").click(function () {
					var name = $(this).data( "name" );
					onShowOnMap(name);
	});
				
	//ACTIVITIES SETUP	
	jQuery('#id_start_date').datepicker({
      showButtonPanel: true
    });
	
	jQuery('#activity_content').carousel({interval : false});
	jQuery("#find_activity_button").click(function (e) {
					e.preventDefault();
					jQuery('#activity_content').carousel('next');
				});
	jQuery("#prev_activities").click(function (e) {
					e.preventDefault();
					jQuery('#activity_content').carousel('prev');
				});
	
	jQuery(".edit_activity").click(function () {
		var activity_id = $(this).data( "activity-id" );
		var name = $(this).data( "activity-name" );
		var start_date = $(this).data( "activity-start-date" );
		var start_time = $(this).data( "activity-start-time" );
		var address = $(this).data( "activity-address" );
		var description = $(this).data( "activity-description" );
		var category = $(this).data( "activity-category" );
		onEditActivity(activity_id, name, start_date, start_time, address, description, category);
	});
	
	
				
	jQuery(".finder-suggestions-table tr td a").click(function(event){
			event.preventDefault();
			$('.finder-suggestions-table tr td a.selected').removeClass('selected');
    		$(this).addClass('selected');
    		var suggested_category = $(this).data( "category" );
    		jQuery("#what").val(suggested_category);
    		//onFinderYelpSearch(suggested_category);
    		
		});
	
	//DISCUSSION SETUP
	jQuery('.activity_summary_content').carousel({interval : false});
	jQuery(".discussion_link").click(function (e) {
		e.preventDefault();
		var activity_id = $(this).data( "activity-id" );
		var carousel_id = '#'+activity_id+'_activity_summary_content';
		jQuery(carousel_id).carousel(2);
	});
	jQuery(".prev_activity_summary").click(function (e) {
		e.preventDefault();
		var activity_id = $(this).data( "activity-id" );
		var carousel_id = '#'+activity_id+'_activity_summary_content';
		jQuery(carousel_id).carousel(0);
	});
	jQuery(".comment_post").click(function () {
		var activity_id = $(this).data( "activity-id" );
		onSaveComment(activity_id);
	});
	
	
	
	//HOTELS SETUP
	jQuery("#finder_hotel_search").click(onFinderExpediaSearch);
	jQuery('#hotel_check_in').datepicker({
      showButtonPanel: true
    });
    jQuery('#hotel_check_out').datepicker({
      showButtonPanel: true
    });
    
    
    jQuery(".nav-options").click(function (e) {
    	e.preventDefault();
    	$(this).tab('show');
    });
    
    
    //REVIEW SETUP
    jQuery(".review_link").click(function (e) {
		e.preventDefault();
		var activity_id = $(this).data( "activity-id" );
		var carousel_id = '#'+activity_id+'_activity_summary_content';
		jQuery(carousel_id).carousel(1);
	});
    jQuery('.star').raty({ 
    	half:true,
    	starOff: STATIC_URL+'trip/star-off.png',
  		starOn : STATIC_URL+'trip/star-on.png',
  		starHalf: STATIC_URL+'trip/star-half.png',
  		size: 24
  		
    });
	  
    
	initialize();
	loadActivityData();
}

jQuery(document).ready(prepareDocument);