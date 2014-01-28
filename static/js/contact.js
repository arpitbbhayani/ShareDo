METHOD_GET = "GET";
METHOD_POST = "POST";

BASE_URL = "http://localhost:8000/sharedo";

function email() {

	var from = "Anonymous";
	var subject = "Subject : ";
	var body = "Body : "

	from = jQuery('#from').val();
	subject += jQuery('#subject').val();
	body += jQuery('#body').val();

	jQuery.ajax({
		url: BASE_URL + '/api/send_email',
		type: METHOD_POST,
		headers: {
			'from' : from,
			 'body': body,
			 'subject': subject
		},
		success: function() {
			window.location.href = '/sharedo/user/index';
		}
	});

	return false;

}