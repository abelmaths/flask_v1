$('button#login').click( function() {
	var username = $('input#username').val()
	attempt_login(username)
})

function attempt_login(username) {
	// Attempts a login via AJAX
	$.ajax( {
      url: '/_login_attempt',
      data: JSON.stringify ({
        'username':username
      }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      type: "POST",
      success: function(response) {
        // Returns status=1 and userID
        var response = JSON.parse(response);
        var status = response['status']
        var data = response['data']
        if (status=='1') {
        	window.location.href = '/my_exercises'
        }
        else {
          alert("Could not log in.")
        }
      },
      fail: function() {
        alert("Server error.")
      } // end success callback
    }); // end ajax

}