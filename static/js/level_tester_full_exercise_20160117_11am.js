/*
TODO
Create some images and put these in (2 hours)
Loop round if all questions finished before level complete (30 min)
Tidy code (1 hour)
(Create homepage - when a link is clicked or dropdown selected, we test this level)
Send to Woody
Add alternative correct answer functionality in Excel

For full exercise (TODO)
------------------------
Each level loaded into DB with some unique ID
An exercise has an array of all of the levels in it
When teacher creates an exercise, store level_id array in pupil's DB entry
When pupil loads exercise page, pull out this level_id array to be used in the page
Load 'exercise' page, including array of all level_hash_list to be loaded
	(note whenever an a level is loaded, count questions and generate random order)
Jquery requests first level and displays to screen (based on random ordering)
Once level is displayed to screen, start collecting next level in background and store to json
Once level complete, load this stored json level
Once level is displayed to screen, start collecting next level in background and store to json
Repeat until last level, in which case don't load next one
Save progress at each level for now (can change to each question if needs be)

Tasks
------------------------
--1) Explore speed of loading up pupil's entry depending how big the pupil's entry is - do we have a problem loading everything every time?
--2) Create DB loading system - when 'save_exercise' is called, save any updated levels to database along with exercise entry (already started this)
3) Update the mongo.py demo script to save an exercise in database and under each pupil's entry
4) Create a test page (with pupil_id and homework_id embedded in javascript for now)
5) Create functionality described above


2016-01-23 tasks
------------------------
Save progress after each question
	--1) Change all logic to happen when 'check' button is pressed
	--2) Send latest snapshot to server when 'check' button pressed
Have something happen when exercise is finished
Randomise order of questions being shown
Create concept of user being logged in, so we can write to their database entry
	Maybe just a simple login page for now where you type your username and then you're logged in
End of homework should also save level progress to database (only end of level currently)
Neaten up javascript code if needs be
Create button to take you out of exercise once homework is complete
Create a 'my homeworks' page for pupil, which will open up an exercise to be done
*/

// GENERAL
function debug(argument) {
	if (true) {
		console.log(argument)
	}
}


// =================== Setting up =======================
function update_questions_correct_required() {
	questions_correct_required = parseInt(level['corrects_required'][0])
}

// =================== Generating strings =====================
String.prototype.format = function() {
	// Allows us to use format function
	// Inputs must be an assoc array, e.g. {'var01':6, 'ans01':4}
	// And then a true|false flag depending if we want to show answer
	// Usage ==> 'one two {var01}'.format({'var01':'three'}, false)

    var formatted = this;
    var D = arguments[0];
    var show_answer = arguments[1];

    for (key in D) {
    	var regexp = new RegExp('\\{'+key+'\\}', 'gi');
    	if (key.substring(0, 3) == 'ans' && show_answer == false) {
    		// Replace answer with a box for pupil to type into
    		formatted = formatted.replace(regexp, '<input id='+key+' data-already-answered="false">');
    	}
    	else {
    		// Insert value into the string
    		formatted = formatted.replace(regexp, D[key]);	
    	}        
    }
    return formatted;
};

function format_strings(string_key, show_answer) {
	// Given a level map, a question number, show_answer flag (for scaffold vs. worked)
	// and string_key (question_text, scaffold_text, hint_text, ans_01_hint_text [etc])
	// Returns array of formatted strings
	var output = []
	var variables = level['variables'][question_number]
	var string_list = level[string_key]
	for (var i = 0; i < string_list.length; i++) {
		var text_string = string_list[i]
		output.push ( text_string.format(variables, show_answer) )
	}
	return output
}

function generate_formatted_array(display_format, answer_key) {
// Display format is one of 'question', 'scaffold', 'worked', 'hint'
// Generate an array with formatted strings depending on question type
	console.log('generate_formatted_array function:')
	console.log('display_format', display_format)
	console.log('answer_key', answer_key)
	if (display_format == 'question') {
		return format_strings(string_key = 'question_text',	show_answer = false)
	}
	if (display_format == 'scaffold') {
		return format_strings(string_key = 'scaffold_text',	show_answer = false)
	}
	if (display_format == 'worked') {
		return format_strings(string_key = 'scaffold_text',	show_answer = true)
	}
	if (display_format == 'hint') {
		return format_strings(string_key = 'hint_text',	show_answer = true)
	}
	if (display_format == 'answer_wrong') {
		return format_strings(string_key = answer_key, show_answer = true)
	}
	if (display_format == 'answer_reveal') {
		return format_strings(string_key = answer_key, show_answer = true)
	}
}

function array_to_html_array(array) {
// Parse each question line as HTML, push into an array
	var html_array = []
	for (var i=0; i<array.length; i++) {
		var html = $.parseHTML(array[i])
		html_array.push(html)
	}
	return html_array
}

// =================== Filling out question content =====================
function array_to_hidden_divs(parent_id, array) {
	// For each line, add a div.
	// If answer is required, have an answer button there
	
	// Empty out the current parent_id
	$('#'+parent_id).empty()

	// First convert <inputs> into HTML
	var array = array_to_html_array(array)

	// Loop through lines
	for (var i=0; i<array.length; i++) {

		// Add a div
		$('<div/>', {
		    id: 'line_'+i,
		    hidden: "hidden"
		}).appendTo('#'+parent_id);	

		// Within the div, add text in a div
		$('<div/>', {
		    id: 'line_'+i+'_text'
		}).appendTo('#line_'+i);
		$('#line_'+i+'_text').append(array[i])

		// Within the div, also add another div (currently unused)
		// $('<div/>', {
		//     id: 'line_'+i+'_somethingelse'
		// }).appendTo('#line_'+i);		
	}
}

function last_line_answered() {
	// Loop through to check if all subquestions within question have been answered
	var already_answered = $($('#content_area_body').children().last().find('input')).attr('data-already-answered')
	return already_answered
}

function show_latest_question(parent_id) {
	// For a parent_id go through content and show divs
	// Until the latest unanswered question
	var found_latest_input = false;
	$('#'+parent_id).children('div').each(function() {
		
		// Show the div if no input found yet
		if (found_latest_input == false) {
			$(this).show()	
		}
		
		// Check if input required in this line
		var line = $(this)
		if(line.find('input').length>=1) {
			// There is an input in this line
			if($(line.find('input')[0]).attr('data-already-answered')=='false') {
				found_latest_input = true;	
			}			
		}		
	})
}

function show_question_if_scaffold() {
	// If scaffold, show all but last line of question
	// TODO: make more robust in case last line of question isn't the answer? Or just enforce this?
	if(['scaffold','worked'].indexOf(display_format) !== -1) {
		$('#optional_question_area_body').empty()
		var question = generate_formatted_array('question')
		for (var i=0; i<question.length-1; i++) {
			$('#optional_question_area_body').append(question[i])
		}
	}
	else {
		$('#optional_question_area_body').empty()
	}
}


// =================== Updating interface ===================
function update_progress_section() {
	// Update the visual progress section (much of it temp for now)
	$('#questions_correct_level_count').text(questions_correct_level_count)
	$('#questions_incorrect_level_count').text(questions_incorrect_level_count)
	$('#questions_correct_total_count').text(questions_correct_total_count)
	$('#questions_incorrect_total_count').text(questions_incorrect_total_count)
	$('#progress_current_question').text(question_number)
	$('#questions_attempted_total_count').text(questions_attempted_count)
	$('#questions_correct_required').text(questions_correct_required)
	$('#questions_attempted_required').text(questions_attempted_required)
}

function hide_or_show_display_format_titles() {
	// Hide or show the original question (if scaffold question, we need to show it)
	if(['start','worked', 'scaffold'].indexOf(display_format) !== -1) {
		$('#optional_question_area').show()
		$('#content_area_title').show()
	}
	else {
		$('#optional_question_area').hide()
		$('#content_area_title').hide()
	}
}

function hide_or_show_hint_button() {
	// Hide or show the hint button according to the display_format
	if(['start','worked', 'scaffold'].indexOf(display_format) !== -1) {
		$('button#hint').hide()
	}
	else {
		$('button#hint').show()
	}
}

// =================== Hint =====================
function prepare_hint_button() {
	// Track whether hint button is clicked
	// When it is clicked, show correct hint text
	hint_used = 'no_hint'
 	$('button#hint').unbind( "click" )
 	$('button#hint').click(function(){		
		var hint_text = generate_formatted_array('hint')[0]
		hint_used = 'hint'
		alert(hint_text)
	})
}

// =================== Checking answer =====================

function isNumber(n) { return /^-?[\d.]+(?:e-?\d+)?$/.test(n); } 

function check_answer(attempted_answer, answer_key) {
	// Checks the answer
	// Compares against known wrong answers
	// Compares against known right answers
	// TODO - add alternative correct answers functionality in Excel, i.e. if more than 1 possible
	// Returns score and commentary message

	// Check what the desired answer is
	var desired_answer = level['variables'][question_number][answer_key]

	// Check if 'answer reveal' exists (i.e. explanation for an answer, rather than default)
	// Create a default one if not
	if (answer_key+'_reveal' in level) {
		var answer_reveal_string = generate_formatted_array('answer_reveal', answer_key+'_reveal')
	} else {
		var answer_reveal_string = 'The answer is '+desired_answer+'.'
	}
	
	// Check if user made a known common mistake
	var wrong_answer_map = level['variables'][question_number][answer_key+'_wrong']
	if (wrong_answer_map) {
		if (attempted_answer_string in wrong_answer_map) {
			wrong_answer_index = wrong_answer_map[attempted_answer]+'_text'
			var answer_wrong_text = generate_formatted_array('answer_wrong', wrong_answer_index)
		return {'score':0,
		'commentary_line_1':"I'm afraid not.",
		'commentary_line_2':answer_wrong_text}
		}
	}	
	
	// If they didn't make a known mistake, we now check if correct or wrong
	// If they typed a number
	if (isNumber(attempted_answer)) {
		// If the answer is not supposed to be a number, break
		if (!isNumber(desired_answer)) {
			return {'score':0,
			'commentary_line_1':"I'm afraid not.",
			'commentary_line_2':'The answer is not a number.'}
		}
		// Now round the number
		var attempted_answer_string = attempted_answer
		var desired_answer_string = desired_answer
		var attempted_answer = parseFloat(attempted_answer)
		var attempted_answer = parseFloat(attempted_answer.toPrecision(3))
		var desired_answer = parseFloat(desired_answer)
		var desired_answer = parseFloat(desired_answer.toPrecision(3))
		
		// Check if user was spot in to this level of significance
		if (attempted_answer == desired_answer) {			
			return {'score':1,
			'commentary_line_1':'You are correct',
			'commentary_line_2':''}
		}

		// Check if user was within margin of error allowed, if one exists
		// TODO, implement properly 
		console.log(typeof desired_answer)
		if (attempted_answer <= desired_answer+1 && attempted_answer >= desired_answer-1) {
			return {'score':1,
			'commentary_line_1':'Almost correct!',
			'commentary_line_2':answer_reveal_string}
		}
	}
	
	// They didn't type a number, so must have typed a string
	else {
		// If they are correct
		if (attempted_answer.toLowerCase() == desired_answer.toLowerCase()) {			
			return {'score':1,
			'commentary_line_1':'You are correct',
			'commentary_line_2':answer_reveal_string}
		}

		// If it was supposed to be a number
		if (isNumber(desired_answer)) {
			return {'score':0,
			'commentary_line_1':"I'm afraid not",
			'commentary_line_2':'The answer is supposed to be a single number.'}
		}
	} 

	// Got here so nothing matches, return 0
	return {'score':0,
	'commentary_line_1':'Sorry, that is not correct.',
	'commentary_line_2':answer_reveal_string}
	
}

function prepare_check_button() {
	// If worked example, we don't want to check - go straight to continue
	if(['start','worked'].indexOf(display_format) !== -1) {		
		prepare_continue_button()
	}
	else {
		$("#check_or_continue").unbind( "click" )
		$('#check_or_continue').text('Check')
		link_check_button('content_area_body')
		bind_check_button(question_number = question_number)
	}
}

function bind_check_button(question_number) {
	// When check button is clicked, make it check the answer
	
	// Get the answer key
	var answer_key = $('#check_or_continue').attr('data-answer')

	// On click, check the answer
	$('#check_or_continue').click(function(){
		
		// Make 'data-already-answered = true' for the appropriate input box
		$('#'+answer_key).attr('data-already-answered', 'true')

		// Check the answer, show commentary
		var attempted_answer = $('#'+answer_key).val()
		var answer_check = check_answer(attempted_answer, answer_key)
		// Returns {'score':0, 'commentary':'This was what you did wrong'}
		
		// Use the score and commentary to update everything
		var score = answer_check['score']
		var commentary_line_1 = answer_check['commentary_line_1']
		var commentary_line_2 = answer_check['commentary_line_2']
		update_temp_score_array(score)
		temp_answer_array.push(attempted_answer)
		show_commentary(commentary_line_1, commentary_line_2)

		// Make 'check' button into 'continue' button
		prepare_continue_button()
	})
}

function link_check_button(parent_id) {
	// Link the 'check' button to the latest answer required
	// TODO - disable button until answer typed

	// Find latest unanswered input
	$('#'+parent_id).children('div').each(function() {
		
		// Check if input required in this line and has not been answered
		// If so, get the answer id and link to the check button
		var input = $(this).find('input')
		if (input.length>=1) {
			// NB assumes only 1 input per line
			// If input has been answered already, continue, otherwise create link
			var already_answered = $(input).attr('data-already-answered')
			if (already_answered=='true') {
				// Do nothing
			}
			else {
				// Set the check button to link
				var id = input[0].id;
				$('#check_or_continue').attr('data-answer', id);
				// Break out of the loop
				return false;
			}		
		}
	})		
}

function choose_next_display_format() {
	debug("Choosing next display format - currently:")
	debug(display_format)
	if (display_format == 'question') {
		if (this_question_score_average()==1) {
			display_format = 'question'
		}
		else {
			display_format = 'scaffold'
		}
	}
	if (display_format == 'scaffold') {
		if (this_question_score_average()==1) {
			display_format = 'question'
		}
		else {
			display_format = 'scaffold'
		}
	}
	if (display_format == 'worked') {
		display_format = 'question'
	}
	if (display_format == 'start') {
		if (level['worked_example_start'][0] == '1') {
			display_format = 'worked'	
		}
		else {
			display_format = 'question'
		}
		
			
	}
}

function update_temp_score_array(score) {
	this_question_score_count.push(score)  // 0 or 1
}

function update_score_counters() {
	questions_correct_total_count += this_question_score_average()
	questions_incorrect_total_count += (1-this_question_score_average())
	questions_attempted_count += 1
	questions_correct_level_count += this_question_score_average()
	questions_incorrect_level_count += (1-this_question_score_average())
}

function reset_temp_score_array() {
	this_question_score_count = []
}

function this_question_score_average() {
	var sum = 0;
	for( var i = 0; i < this_question_score_count.length; i++ ){
	    sum += this_question_score_count[i]
	}
	return sum*1.0 / this_question_score_count.length
}

function create_answer_log() {
	// Create log of answer give
	answer_log = {
		'qu':question_number,
		'level':level_number,
		'score':this_question_score_average(),
		'df':display_format,
		'hint':hint_used,
		'ans':temp_answer_array
	}
}

function reset_temp_answer_array() {
	temp_answer_array = []
}

// =================== Checking progress =====================
function check_stage() {
	// If mid question we catch this in a different place (with last_line_finished())
	if (questions_attempted_count >= questions_attempted_required) {
		stage = 'end_of_homework'
	}

	else if (questions_correct_level_count < questions_correct_required) {
		stage = 'end_of_question'
	}

	else if (questions_correct_level_count >= questions_correct_required) {
		// End of homework if completed all levels
		if (level_number == max_level_number) {
			stage = 'end_of_homework'
		}
		// Otherwise end of level
		else {
			stage = 'end_of_level'	
		}		
	}
	return stage
}

function update_level_and_question_tickers() {
	// Update the level and question tickers
	// Allows us to save a snapshot of current state
	if (stage == 'end_of_question') {
		question_number += 1
	}
	else if (stage == 'end_of_level') {
		question_number = 0
		level_number += 1
		questions_correct_level_count = 0
    	questions_incorrect_level_count = 0
	}
	else if (stage == 'end_of_homework') {
		alert('Do we need to do something here?')
	}
}



// =================== Continue button =====================
function continue_next_question() {
	// Pressed continue, now get the next question ready
	update_progress_section()
	//display_format = choose_next_display_format()
	debug("The display format has been updated:")
	debug(display_format)
	hide_or_show_display_format_titles()
	hide_or_show_hint_button()
	prepare_hint_button()
	reset_temp_score_array()
	question = generate_formatted_array(display_format)
	show_question_if_scaffold()
	array_to_hidden_divs('content_area_body', question)
	show_latest_question('content_area_body')
	prepare_check_button()
}

function continue_same_question() {
	console.log("Continuing same question")
	prepare_check_button()
	show_latest_question('content_area_body')
}

function continue_next_level() {
	question_number = 0 
	// Get the next level from the database
	get_level_from_db_and_start_level(
		level_hash_list[level_number]
		)
	//$('#commentary_area').text("Level complete - now we would fetch next level from server")
}

function continue_homework_complete() {
	$('#commentary_area').text("Homework complete - now we would exit homework and save to server etc.")
}

function prepare_continue_button() {
	// Get rid of functionality, change text on button
	$("#check_or_continue").unbind( "click" )
	$('#check_or_continue').text('Continue')
	
	// Check if mid-question (i.e. scaffold) - don't change question
	if (last_line_answered()=="false") {
		$('#check_or_continue').click(function(){
			clear_commentary()
			// Note, since we don't save progress here, in theory you could reload page
			// and not get penalised for wrong answer
			continue_same_question()
			return false
		})
	}
	// Check if worked example - simple go to next question
	else if(['start','worked'].indexOf(display_format) !== -1) {
		$('#check_or_continue').click(function(){
			create_answer_log()
			stage = check_stage()
			update_level_and_question_tickers()
			choose_next_display_format()
			save_progress()
			continue_next_question()
		})
	}
	// Otherwise go to next question or level or finish homework
	else {
		// Update scores to find out what button should do
		update_score_counters()
		update_progress_section()
		create_answer_log()
		reset_temp_answer_array()
		// Check what stage we are at (end_of_question, end_of_level, end of homework) - affects button funcitonality
		stage = check_stage()
		update_level_and_question_tickers()
		choose_next_display_format()
		save_progress()
		// Bind click action accordingly
		$('#check_or_continue').click(function(){
			clear_commentary()
			if (stage == 'end_of_question') {
				continue_next_question()
			}
			if (stage == 'end_of_level') {
				continue_next_level()
			}
			if (stage == 'end_of_homework') {
				continue_homework_complete()
			}
		})
	}
}

function show_commentary(commentary_line_1, commentary_line_2) {
	$('#commentary_line_1').text(commentary_line_1)
	$('#commentary_line_2').text(commentary_line_2)
}

function clear_commentary() {
	$('#commentary_line_1').empty()
	$('#commentary_line_2').empty()
}

// =================== Starting a new level ===================
function begin_level_sequence() {
	update_questions_correct_required()
	update_progress_section()
	continue_next_question()
}

// =================== Loading and saving progress ==========================
function load_progress_as_of_last_saved() {
	if (progress_snapshot == 0) {
		// No progress, load from the start of level
		// Note that these values are already filled out
		return true
	}
	else {
		level_number = progress_snapshot[0]
		question_number = progress_snapshot[1]
		display_format = progress_snapshot[2]
		questions_correct_total_count = progress_snapshot[3]
		questions_incorrect_total_count = progress_snapshot[4]
		questions_correct_level_count = progress_snapshot[5]
		questions_incorrect_level_count = progress_snapshot[6]
	}
}

function save_progress() {
	// Save user's current progress to server
	// If homework has just ended, reset it
	debug("Calling server to save progress snapshot")
	if (stage == 'end_of_homework') {
		var progress_snapshot = '0'
	}
	else {
		var progress_snapshot = [
			level_number,
			question_number,
			display_format,
			questions_correct_total_count,
			questions_incorrect_total_count,
			questions_correct_level_count,
			questions_incorrect_level_count,
			question_order_array
		]
	}
	debug("This is the progress we are sending:")
	debug(progress_snapshot)
	debug("This is the answer log we are sending:")
	debug(answer_log)
	$.ajax( {
      url: '/_save_progress',
      data: JSON.stringify ({
        'progress_snapshot':progress_snapshot,
        'answer_log':answer_log
      }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      type: "POST",
      success: function(response) {
        // Returns status=1 and userID
        var response = JSON.parse(response);
        var status = response['status']
        var level_blob = response['data']
        if (status=='1') {
        	debug("Successfully saved progress to server")      
        }
        else {
          alert("DID NOT SAVE NOT PROGRESS TO SERVER")
        }
      },
      fail: function() {
        alert("Server error")
      } // end success callback
    }); // end ajax
}

// =================== AJAX calls =====================

function get_level_from_db_and_start_level(next_level_hash) {
	// Provides server with level_id, will return json
	debug("Get the next level")
	$.ajax( {
      url: '/_get_level_blob',
      data: JSON.stringify ({
        'next_level_hash':next_level_hash
      }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      type: "POST",
      success: function(response) {
        // Returns status=1 and userID
        var response = JSON.parse(response);
        var status = response['status']
        var level_blob = response['data']
        if (status=='1') {

          // Saved successfully and got next level
          //level_number += 1 // Done elsewhere
          level = level_blob

          // Once the level is loaded, start the level sequence
          begin_level_sequence()          

        }
        else {
          console.log("Could not load level.")
        }
      },
      fail: function() {
        alert("Server error")
      } // end success callback
    }); // end ajax
}


// Variables tracking # correct and # wrong
var this_question_score_count = []
var questions_correct_required = 4
var questions_correct_total_count = 0
var questions_incorrect_total_count = 0
var questions_correct_level_count = 0
var questions_incorrect_level_count = 0
var questions_attempted_count = 0
var questions_attempted_required = 10
var stage = ''; //'end_of_question', 'mid_question', 'end_of_level'
var question_number = 0
var display_format = 'worked'
var level = ''
var answer_log = {}
var hint_used = 'hint'
var question_order_array = []
var temp_answer_array = []  // For storing answers given to each question

//var level_hash_list = from html template via Jinja
var max_level_number = (level_hash_list.length)-1
var level_number = 0
load_progress_as_of_last_saved()
get_level_from_db_and_start_level(level_hash_list[level_number])












