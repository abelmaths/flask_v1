function bind_elements() {

	// Login button
	$('#login_button').click( function() {
		variables = {
			'username' : $('#login_username_input').val(),
			'password' : $('#login_password_input').val()
		}
		ajax_wrapper(
			'/_login_attempt',
			variables,
			login_success
		)
	})
}

function login_success() {
	hide_body_and_redirect('/my_exercises')
}

bind_elements()