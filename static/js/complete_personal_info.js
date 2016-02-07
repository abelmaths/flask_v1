function bind_elements() {
	// Signup button
	$('#submit_personal_info_button').click( function() {
	  variables = {
			'firstname' : $('#firstname_input').val(),
			'surname' : $('#surname_input').val(),
			'display_name' : $('#display_name_input').val()
		}
		ajax_wrapper(
			'/_submit_personal_info',
			variables,
			submit_personal_info_success
		)
	})
}

function submit_personal_info_success() {
	hide_body_and_redirect('/my_exercises')
}

bind_elements()