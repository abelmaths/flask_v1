function bind_elements() {
	// When anything typed in inputs, update classroom name preview
	$('input').keyup( function() {
	  update_classroom_name_preview()
	})

	// When classroom create attempt made, use AJAX and load success page
	$('#create_classroom_button').click( function() {
		variables = {
			'class_name' : $('#class_name_input').val(),
			'subject' : $('#subject_input').val()
		}
		ajax_wrapper(
			'/_create_classroom_submit',
			variables,
			create_classroom_success
			//{'out':'#create_classroom_view', 'in':'#classroom_created_success_view'}
		)
	})
}

function create_classroom_success(data, success_variables) {
	// Populate classroom code span with the entry code from AJAX
	$('#classroom_code').text(data['classroom_code'])
	// Bring in correct part of page
	//hide_and_show(success_variables['out'], success_variables['in'])
	hide_and_show('#create_classroom_view', '#classroom_created_success_view')
}

function update_classroom_name_preview() {
	var class_name = $('#class_name_input').val()
	var subject = $('#subject_input').val()
	$('#class_name_preview').text(class_name)
	$('#subject_preview').text(subject)
}

bind_elements()