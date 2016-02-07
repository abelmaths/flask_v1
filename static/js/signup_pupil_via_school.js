function bind_elements() {
	// Signup button
	$('#signup_button').click( function() {
	  variables = {
			'username' : $('#signup_username_input').val(),
			'password' : $('#signup_password_input').val(),
			'firstname' : $('#signup_firstname_input').val(),
			'surname' : $('#signup_surname_input').val(),
			'entry_code' : entry_code  // Passed via flask
		}
		ajax_wrapper(
			'/_create_pupil_via_school',
			variables,
			create_pupil_via_school_success
		)
	})

	$('#show_login_button').click( function() {
		alert("Show login section here") //TODO
	})
}

function create_pupil_via_school_success() {
	hide_body_and_redirect_with_flash('pupil_all_exercises', 'Congratulations! You have successfully joined the classroom.')
}

bind_elements()