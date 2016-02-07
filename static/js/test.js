function tester(message) {
	console.log(message)
}

function outer(fn) {
	fn()
}

outer(function(){tester('hey hey')})