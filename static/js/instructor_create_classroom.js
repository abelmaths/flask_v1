$('input').keyup( function() {
  update_classroom_name_preview()
})

function update_classroom_name_preview() {
  var class_name = $('#class_name_input').val()
  var subject = $('#subject_input').val()
  $('#class_name_preview').text(class_name)
  $('#subject_preview').text(subject)
}
