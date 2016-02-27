function bind_elements() {
	// I'm a teacher/student buttons
	$('#submit_entry_code_button').click( function() {
	  attempt_to_join_classroom()
	})
}

function attempt_to_join_classroom() {
	var entry_code = $('#entry_code_input').val()
	hide_body_and_redirect('/entry/'+entry_code)
}

bind_elements()