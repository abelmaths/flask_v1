function bind_elements() {
	// Signup button
	$('#join_classroom_button').click( function() {
	  variables = {
			'entry_code' : entry_code  // Passed via flask
		}
		ajax_wrapper(
			'/_pupil_join_classroom_confirm',
			variables,
			pupil_join_classroom_success
		)
	})
}

function pupil_join_classroom_success() {
	hide_body_and_redirect_with_flash('pupil_all_exercises', 'Congratulations! You have successfully joined the classroom.')
}

bind_elements()