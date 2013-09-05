//function that is called when save is pressed on the modal
function onInvite(user_pk){
	// build an object of review data to submit
	var invitation = { 
		user_pk: user_pk,
		slug: jQuery("#id_slug").val() };
	// make request, process response
	jQuery.post("/invite/send_invite/", invitation,
		function(response){
			if(response.success == "True"){
				
			}
			else{
			}
		}, "json");
}
