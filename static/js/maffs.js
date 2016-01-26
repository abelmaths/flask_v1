console.log("HELLO MAFFS")
function bind_clicks() {
  // This will invite a user by email when submit pressed
  $('#submit_answer').click( function(evt) {
    evt.preventDefault();
    evt.stopImmediatePropagation();
    check_if_correct()
    submit_answer()
  }) // end submit
}

function check_if_correct() {
	console.log("Checking if correct")
}

function submit_answer() {
	console.log("Submitting answer")
	var answer = $('#the_answer').val()
	console.log("you entered -->", answer)
	$.ajax( {
      url: '/_question_submit',
      data: JSON.stringify ({
        'correct':1,
        'answer':answer
      }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      type: "POST",
      success: function(response) {
        // Returns status=1 and userID
        response = JSON.parse(response);
        status = response['status']
        data = response['data']
        if (status=='1') {
          console.log("Status = 1, hurray")
          console.log("This is the data:", data)
        }
        else {
          console.log("There was an error")
        }
      },
      fail: function() {
        alert("Server error")
      } // end success callback
    }); // end ajax
}

bind_clicks()