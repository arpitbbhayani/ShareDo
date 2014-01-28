var c = 0;

function validate_name ( name_obj ) {

	if (name_obj.val().length == 0 ) {
		jQuery("#availability").attr('class' , 'centered error');
        jQuery("#availability").html("Nickname should not be blank");
		return 0;
	}
	return 1;
}

function validate_email ( email_obj ) {
	if ( email_obj.val().match("[a-zA-Z].*[@][a-z]+[.][a-z]+") == null ) {
		jQuery("#availability").attr('class' , 'centered error');
        jQuery("#availability").html("Invalid email id");
		return 0;
	}
	else {
		return 1;
	}
	return 1;
}

function validate_pass ( pass_obj , pass_c_obj ) {

	var pass = pass_obj.val();

	if ( pass.length == 0 ) {
		return 0;
	}
	else {

		if ( pass_obj.val() != pass_c_obj.val() ) {
			jQuery("#availability").attr('class' , 'centered error');
            jQuery("#availability").html("Passwords do not match");
			return 0;
		}
		else {
			return 1;
		}
	}

}

function validate_form( form ) {
	var n = validate_name (jQuery('#name'));
	var e = validate_email (jQuery('#email_id'));
	var p = validate_pass (jQuery('#pwd'), jQuery('#pass_c'));

	if ( n == 1 && e == 1 && p == 1 && c == 1 ) {
		return true;
	}
	else {
		return false;
	}
}


jQuery(document).ready(function() {

    jQuery("#name").focusout(function() {
	    val = jQuery("#name").val();
	    if ( val != "" ) {
            is_user_present(val);
        }
        else {
            jQuery("#availability").attr('class' , 'centered error');
            jQuery("#availability").html("Nickname should not be blank");
        }


    });

});

function is_user_present(val) {
	jQuery.ajax({
            url:BASE_URL + "/api/user_present",
			type: METHOD_POST,
			headers: {
                'val': val
			},
			success: function(resp) {
				if( resp == "True" ) {
				    c = 0;
				    jQuery("#availability").attr('class' , 'centered error');
                    jQuery("#availability").html( val + " already registered.");
				}
				else {
				    c = 1;
				    jQuery("#availability").attr('class' , 'centered ok');
                    jQuery("#availability").html(val + " is available");
				}
			}
		});
};