TWITTER_CONS_KEY = "rGmgLbYUw2Au7UUrQAjnfQ";
TWITTER_CONS_SEC = "yXIPMf6PHoaAgZZnhBQV7AhJG40kpXgif1V3hejqo";

METHOD_GET = "GET";
METHOD_POST = "POST";

BASE_URL = "http://localhost:8000/sharedo";

var oauth_token = "";
var oauth_token_secret = "";

jQuery(document).ready(function () {

	OAuth.initialize('FGmDXTT3mfmJlnuLalH2Mp83fVw');
	jQuery('#blink').click(blink);
	jQuery('#add_blink').show();
	jQuery('#add_a_blink').hide();

});

function cancel_blink() {
	jQuery('#add_blink').hide();
	jQuery('#add_a_blink').show();
	jQuery('#blink_add_event_input').val('');
	jQuery('#blink_add_event_select').html('');
	jQuery('#blink_add_event_action').html('');
}

function add_a_blink() {
	jQuery('#add_blink').show();
	jQuery('#add_a_blink').hide();
}

function blink() {
	jQuery.ajax({
		url: BASE_URL + '/api/apply_all_blinks',
		type: METHOD_POST,
		success: function() {
			console.log('Scanning Completed!');
		}
	});
}

function generate_oauth_signature(httpMethod, url, sorted_params) {
	var complete_str = httpMethod + "&" + encodeURI(url) + "&";

	var encoded_params = '';
	for(key in sorted_params) {
		encoded_params += (encodeURI(key) + '%3D' + encodeURI(sorted_params[key]));
	}

	encoded_params += '%26';
	encoded_params += '%26';
	complete_str += encoded_params;

	var signing_key = TWITTER_CONS_SEC + "&" + oauth_token_secret;
	var hash = CryptoJS.HmacSHA1(complete_str, signing_key);

	return hash;
}

function login(type, provider) {
	OAuth.popup(provider, function(error, result) {
		oauth_token = (result.oauth_token) ? result.oauth_token : result.access_token;
		oauth_token_secret = (result.oauth_token_secret) ? result.oauth_token_secret : result.refresh_token;

		jQuery.ajax({
			url:BASE_URL + "/api/new_token",
			type: METHOD_POST,
			headers: {
				'oauth_token': oauth_token,
				'oauth_token_secret': oauth_token_secret,
				'provider': provider
			},
			success: function() {
				if ( type == 'event' ) {
					jQuery('#event_message').html(get_event_html(provider));
				}
				else if ( type == 'action' ) {
					jQuery('#action_message').html(get_action_html(provider));
				}
			}
		});
	});
};

function event_changed( value ) {
	var index = parseInt(value.split('_')[1])
	jQuery('#blink_add_event_input').attr('placeholder' , events_info[ index ].in_query);
	if ( events_info[ index ].in_query == "" ) {
		jQuery('#blink_add_event_input').hide();
	}
	else {
		jQuery('#blink_add_event_input').show();
	}
}

function initialize_events( provider ) {
	jQuery.ajax({
		url:BASE_URL + "/api/events",
		type: METHOD_POST,
		headers: {
			'provider': provider
		},
		success: function( data ) {
			var obj = eval ("(" + data + ")");
			/* For events */
				events_info = eval ("(" + obj.events + ")");
				for ( var i = 0 ; i < events_info.length ; i+=1 ) {
					jQuery("#blink_add_event_select").append('<option value="'+events_info[i].id+'_'+i+'">'+events_info[i].one_liner+'</option>');
				}
				if ( events_info.length > 0 ) {
					jQuery("#blink_add_event_select").attr('onClick' , 'event_changed(this.value);');
					event_changed( events_info[0].id + "_" + 0);
				}
		}
	});
}

function initialize_actions( provider ) {
	jQuery.ajax({
		url:BASE_URL + "/api/actions",
		type: METHOD_POST,
		headers: {
			'provider': provider
		},
		success: function( data ) {
			var obj = eval ("(" + data + ")");
			/* For Actions */
				var actions_info = eval ("(" + obj.actions + ")");
				for ( var i = 0 ; i < actions_info.length ; i+=1 ) {
					jQuery("#blink_add_action_select").append('<option value="'+actions_info[i].id+'">'+actions_info[i].one_liner+'</option>');
				}
		}
	});
}


function get_event_html( provider ) {

	var str = '<div class="event_text">When ';

	initialize_events(provider);
	var id = 'blink_add_event_select';
	str += ('<select class="styled-select blink_add_select" id=' + id + '>"');
	str += '</select>';

	str += ('on ' + provider );

	/*if ( provider == 'facebook' ) {
		str += ' with ' + '<select class="blink_add_select"><option>Hashtag</option></select>';
	}*/

	str += ('&nbsp;&nbsp;&nbsp;<input type="text" class="blink_add_input" id="blink_add_event_input"/>');

	str += '</div>';

	return str;
}

function get_action_html( provider ) {

	var str = '<div class="action_text">';

	initialize_actions(provider);
	var id = 'blink_add_action_select';
	str += ('<select class="styled-select blink_add_select" id=' + id + '>"');
	str += '</select>';

	str += ('on ' + provider );

	str += '</div>';

	return str;
}

function provider_selected( provider ) {
	if(provider == 'event_instagram') {
		jQuery.ajax({
			url:BASE_URL + "/api/is_user_authorized",
			type: METHOD_POST,
			headers: {
				'provider': 'instagram'
			},
			success: function( data ) {
				if ( data == 'True' ) {
					jQuery('#event_message').html(get_event_html('instagram'));
				}
				else {
					login('event', 'instagram');
				}
			}
		});
	}
	else if ( provider == 'event_facebook' ) {
		/*jQuery.ajax({
			url:BASE_URL + "/api/is_user_authorized",
			type: METHOD_POST,
			headers: {
				'provider': 'facebook'
			},
			success: function( data ) {
				if ( data == 'True' ) {
					jQuery('#event_message').html(get_event_html('facebook'));
				}
				else {
					login('event', 'facebook');
				}
			}
		});*/

		window.location.href = 'under_construction';

	}
	else if ( provider == 'event_twitter' ) {
		jQuery.ajax({
			url:BASE_URL + "/api/is_user_authorized",
			type: METHOD_POST,
			headers: {
				'provider': 'twitter'
			},
			success: function( data ) {
				if ( data == 'False' ) {
					login('event', 'twitter');
				}
				else {
					jQuery('#event_message').html(get_event_html('twitter'));
				}
			}
		});
	}
	else if ( provider == 'action_facebook' ) {
		jQuery.ajax({
			url:BASE_URL + "/api/is_user_authorized",
			type: METHOD_POST,
			headers: {
				'provider': 'facebook'
			},
			success: function( data ) {
				if ( data == 'True' ) {
					jQuery('#action_message').html(get_action_html('facebook'));
				}
				else {
					login('action', 'facebook');
				}
			}
		});
	}
	else if ( provider == 'action_twitter' ) {
		jQuery.ajax({
			url:BASE_URL + "/api/is_user_authorized",
			type: METHOD_POST,
			headers: {
				'provider': 'twitter'
			},
			success: function( data ) {
				if ( data == 'True' ) {
					jQuery('#action_message').html(get_action_html('twitter'));
				}
				else {
					login('action', 'twitter');
				}
			}
		});
	}
	else {
		alert('other');
	}
}

function save_blink() {

	var isValid = false;

	var e_select = jQuery('#blink_add_event_select').val();
	var a_select = jQuery('#blink_add_action_select').val();
	var e_input  = jQuery('#blink_add_event_input').val();

	if ( e_select == null || a_select == null ) {
		jQuery('#availability').html('No event or action specified');
	}
	else if ( e_input == null || e_input == "" ) {
		var isVisible = jQuery('#blink_add_event_input').is(':visible');
		if ( isVisible == true ) {
			jQuery('#availability').html('Please enter ' + jQuery('#blink_add_event_input').attr('placeholder') );
		}
		else {
			isValid = true;
		}
	}
	else{
		isValid = true;
	}

	if ( isValid == true ) {
		add_blink();
		jQuery('#add_blink').hide();
		jQuery('#add_a_blink').show();
	}

}

function act( a_obj , action ) {
	id = a_obj.getAttribute('class').split(' ')[1];
	if ( action == "apply" ) {
		apply_blink(id);
	}
	else if ( action == "delete" ) {
		delete_blink(id);
	}
	else {
		alert('Other Action');
	}

}

function apply_blink( id ) {
	jQuery.ajax({
		url:BASE_URL + "/api/apply_blink",
		type: METHOD_POST,
		headers: {
			'blink_id' : id
		},
		success: function( data ) {
			window.location.reload();
		}
	});
}

function delete_blink( id ) {
	jQuery.ajax({
		url:BASE_URL + "/api/delete_blink",
		type: METHOD_POST,
		headers: {
			'blink_id' : id
		},
		success: function( data ) {
			window.location.reload();
		}
	});
}

function add_blink() {
	var e_select = jQuery('#blink_add_event_select').val().split('_')[0];
	var a_select = jQuery('#blink_add_action_select').val().split('_')[0];;
	var e_input  = jQuery('#blink_add_event_input').val();

	e_input = e_input.replace('#','');

	jQuery.ajax({
		url:BASE_URL + "/api/add_blink",
		type: METHOD_POST,
		headers: {
			event_id : e_select,
			in_data : e_input,
			action_id: a_select
		},
		success: function( data ) {
			window.location.reload();
		}
	});
}