BASE_URL = "http://localhost:8000/sharedo";
METHOD_GET = "GET";
METHOD_POST = "POST";

function user_logout() {
	jQuery.ajax({
            url:BASE_URL + "/api/logout",
			type: METHOD_POST,
			headers: {

			},
			success: function() {
				window.location.href = BASE_URL;
			}
		});
};