function bind_elements() {
	// Signup button
	$('#signup_button').click( function() {
	  variables = {
			'email' : $('#signup_email_input').val(),
			'password' : $('#signup_password_input').val(),
			'firstname' : $('#signup_firstname_input').val(),
			'surname' : $('#signup_surname_input').val(),
		}
		ajax_wrapper(
			'/_create_pupil_independent',
			variables,
			create_pupil_independent_success
		)
	})
}

function create_pupil_independent_success() {
	hide_body_and_redirect('/my_exercises')
}

bind_elements()