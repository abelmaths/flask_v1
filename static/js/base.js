
// General functions to consider:
// - AJAX wrapper
// - Fade in page (optional)
// - Fade out page and load another page
// - Analytics logging


function ajax_wrapper_test(endpoint, variables, success_function) {
  success_function()
  alert('gotit')
}

function ajax_wrapper(endpoint, variables, success_function, success_variables) {
	// AJAX wrapper. Supply:
  // - endpoint (must match with Flask app endpoint)
  // - variables map (sent to Python)
  // - success_function (what to do in case of success, given returned data map and success_variables map)
  // - success_variables (map passed to success function in addition to returned AJAX data map)
	$.ajax( {
      url: endpoint,
      data: JSON.stringify (variables, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      type: "POST",
      success: function(response) {
        // Returns status=1 if all OK, status=0 otherwise
        var response = JSON.parse(response);
        var status = response['status']
        var data = response['data']
        if (status=='1') {
        	success_function(data, success_variables)
        }
        else if (status=='0') {
          alert("Should add flash message with 'data.message' message in it --> "+data['message'])
        }
        else {
          alert("Should add flash message with generic error message in it")
        }
      },
      fail: function() {
        alert("Should add flash message with 'server error' message in it")
      } // end success callback
    }); // end ajax
}

function hide_and_show(hide, show) {
  delay = 200
  // Fade out the initial element
  $(hide).fadeTo(delay, 0)
  // Once this is done, hide it and fade in the next one
  setTimeout( function() {
    $(hide).hide();
    $(show).fadeTo(delay, 1)
  }, delay+1)
}

function hide_body_and_redirect(redirect) {
  delay = 200
  // Fade out the initial element
  $('body').fadeTo(delay, 0)
  // Once this is done, hide it and fade in the next one
  setTimeout( function() {
    window.location.href = redirect
  }, delay+1)
}

function hide_body_and_redirect_with_flash(redirect_url_for, flash_message) {
  delay = 200
  // Fade out the initial element
  $('body').fadeTo(delay, 0)
  // Once this is done, hide it and fade in the next one
  setTimeout( function() {
    window.location.href = '/redirect_with_flash/'+redirect_url_for+'/'+flash_message
  }, delay+1)
}

$('#tester').click( function() {
  //hide_body_and_redirect_with_flash('entry', 'This is a flash message')
  alert('test stuff here')
})

// $('.its-a-date').replaceWith(
//     moment(this.textContent).calendar(null, {
//       sameDay: '[Today]',
//       nextDay: '[Tomorrow]',
//       nextWeek: 'dddd',
//       lastDay: '[Yesterday]',
//       lastWeek: '[Last] dddd',
//       sameElse: 'DD/MM/YYYY'
//     })  
//  )

function datatable_link(data) {
    // See http://jsfiddle.net/rp0zw8rm/1/
    // Within a datatable setup, call the following:
    // { 
    //     "data": "name_of_column",
    //     "render" : function(data, type, row, meta){ return datatable_link(data) }
    // }
    // Must ensure that data is in the format 'name_of_column':{'text':'Jack A', 'url':'../12903701293'}
    return $('<a>')
        .attr('href', data['url'])
        .text(data['text'])
        .wrap('<div></div>')
        .parent()
        .html();
}
