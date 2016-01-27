$('button#login').click( function() {
	var username = $('input#username').val()
  var password = $('input#password').val()
  console.log(username)
  console.log(password)
	attempt_login(username, password)
})

function attempt_login(username, password) {
	// Attempts a login via AJAX
	$.ajax( {
      url: '/_login_attempt',
      data: JSON.stringify ({
        'username':username,
        'password':password,
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
          alert(data)
        }
      },
      fail: function() {
        alert("Server error.")
      } // end success callback
    }); // end ajax

}