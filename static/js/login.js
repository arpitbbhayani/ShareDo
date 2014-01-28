BASE_URL = "http://localhost:8000/sharedo";
METHOD_GET = "GET";
METHOD_POST = "POST";

function validate_pass ( pass_obj ) {

	if ( pass_obj.val().length == 0 ) {
	    jQuery("#availability").attr('class' , 'centered error');
        jQuery("#availability").html("Password - cannot be blank");
		return 0;
	}
	return 1;
}

function validate_email ( email_obj ) {

	if ( email_obj.val().length == 0 ) {
		jQuery("#availability").attr('class' , 'centered error');
        jQuery("#availability").html("Username - cannot be blank");
		return 0;
	}
	return 1;
}

function validate_form() {
	console.log('hello');

	var p = validate_pass (jQuery('#pass_c'));
	var e = validate_email (jQuery('#email_id'));

	if ( e == 1 && p == 1 ) {
		return true;
	} else {
		return false;
	}
}

jQuery(document).ready(function() {
	jQuery('#login_form').submit(validate_form);

});