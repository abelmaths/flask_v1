function bind_elements() {
	// I'm a teacher/student buttons
	$('#im_a_student_button').click( function() {
	  hide_and_show('#welcome_view', '#pupil_signup_view')
	})

	$('#im_a_teacher_button').click( function() {
	  hide_and_show('#welcome_view', '#teacher_signup_view')
	})

	$('#im_a_parent_button').click( function() {
	  hide_and_show('#welcome_view', '#parent_signup_view')
	})

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

	// Teacher signup button
	$('#signup_teacher_signup_button').click( function() {
		variables = {
			'email' : $('#signup_teacher_email_input').val(),
			'password' : $('#signup_teacher_password_input').val(),
			'firstname' : $('#signup_teacher_firstname_input').val(),
			'surname' : $('#signup_teacher_surname_input').val(),
			'display_name' : $('#signup_teacher_display_name_input').val(),
		}
		// TODO: check valid email address
		ajax_wrapper(
			'/_create_teacher_attempt',
			variables,
			create_teacher_success
		)
	})

	// Student enter code signup button
	$('#signup_pupil_entry_code_button').click( function() {
	  var entry_code = $('#signup_pupil_entry_code_input').val()
	  hide_body_and_redirect('/entry/'+entry_code)
	})

	// Student independent entry signup button
	$('#signup_pupil_independent_button').click( function() {
	  hide_body_and_redirect('/entry/independent')
	})
	
}

function login_success() {
	hide_body_and_redirect('/my_exercises')
}

function create_teacher_success() {
	hide_body_and_redirect('/my_exercises')	
}

bind_elements()