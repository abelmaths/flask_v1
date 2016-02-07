function bind_elements() {
	// When exercise create submitted
	$('#create_homework_button').click( function() {
		variables = {
			'classroom_id' : $('#classroom_id_select').val(),
			'exercise_id' : $('#exercise_id_select').val(),
			'date_set' : $('#date_set_input').val(),
			'date_due' : $('#date_due_input').val(),
			'attempts_required' : $('#attempts_required_select').val(),
			'pupil_list' : null,
			'exclude_include' : null,
		}
		ajax_wrapper(
			'/_create_homework_submit',
			variables,
			create_homework_success
		)
	})

	$('#advanced_options_toggle').click( function() {
		$('#advanced_options_container').toggle('show')
	})
}

function create_homework_success() {
	alert("Yes!")
}

bind_elements()