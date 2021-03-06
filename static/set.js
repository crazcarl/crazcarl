var score = 0;
var setStart;
var clock;
var clock_running = 0;
// Right now this is going to work in continuous mode
$(document).ready(function() {



	// tile clicked
	$('.tileImg').click(cellClick);
	
	// reset clicked
	$('#reset').click(resetClick);
	
	// submit score clicked
	$('#subScore').click(scoreClick);
	
	setStart = Date.now();
	clock = $('#clock').FlipClock(300,{
		clockFace: 'MinuteCounter',
		autoStart: 0,
		countdown: true,
		callbacks: {
			stop: function () {
            console.log('stopping the clock');
			
        }}
	});
	

});


var cellClick = function() {
	
	// Start timer
	if (!clock_running) {
		clock.start();
		clock_running = 1;
	}
	
	// (un)highlight the cell
	$('#'+this.id).toggleClass('highlight');
	
	// get rid of the message (if one is there) and set score text to black
	$('#message').delay(33).fadeOut();
	$('#score').css({'color':'black'});
	
	if ($('.highlight').length > 2) {
		
		// Get all three elements values and current tile #
		var setAr = [];
		var count = 0;
		$('.highlight').each(function() {
			var tempInt = parseInt(String($(this).attr('src').slice(13,15))); //TODO: update when using static images
			setAr.push(tempInt);
		});

		// Only hit server for wins.
		if (!evaluate(setAr)) {
			$('#message').text('try harder').css({'color':'red'});
			$('#message').delay(45).fadeIn('fast');
			$('.highlight').removeClass('highlight');
			return "";
		}
		
		// Verify legit set
		var data = {"0":setAr[0],"1":setAr[1],"2":setAr[2]};
		$.ajax({
			type: "POST",
			url: "/checkset",
			data: data,
			dataType: 'json',
			success: function(data) {
				// Un-highlight everything
				$('.highlight').removeClass('highlight');
				
				if (data['result']) {
					// Update Score
					score = data['score'];
					$('#score').text(score);
					$('#message').text('yeah, buddy!').css({'color':'green'});
					$('#message').delay(45).fadeIn('fast');
					nextRound(setAr,data['newBoard']);
				}
				else {  //Just in case
					$('#message').text('try harder').css({'color':'red'});
					$('#message').delay(45).fadeIn('fast');
				}

			}
		});
	}
}

		
// Initializes next round upon successful set	
var nextRound = function(setAr,newAr) {

			if (!setAr) {
				return "";
			}
			

			
			// Calculate time
			var time = (Date.now() - setStart) / 1000;
			setStart = Date.now();  // Reset Timer
			// Calculate points
			var points = 1;
			console.log(newAr);
			var tile0 = newAr.indexOf(setAr[0]);
			$('#tile'+tile0).attr('src','/static/imgs/'+pad(newAr[12],2)+'.gif');
			
			var tile1 = newAr.indexOf(setAr[1]);
			$('#tile'+tile1).attr('src','/static/imgs/'+pad(newAr[13],2)+'.gif');
			
			var tile2 = newAr.indexOf(setAr[2]);
			$('#tile'+tile2).attr('src','/static/imgs/'+pad(newAr[14],2)+'.gif');
			
			// Log set to screen
			var imgs = imageHandler(setAr[0],setAr[1],setAr[2]);
			
			var setStr = '<tr class="smallSet"><td style=\'width:50%\'>' + imgs + '</td>'     // imgs
			setStr +=    '<td style=\'width:25%\'>' + time + '</td>'	     // seconds
			setStr +=    '<td style=\'width:25%\'>' + points + '</td></tr>'  // points
			$('#setsTable > tbody:first').prepend(setStr);
			
			if ($('.smallSet').length > 10) {
				$('.smallSet').last().remove()
			}
			
	};



var resetClick = function() {

	var data = {};
	var sets = setCheck();
	if (sets.length > 0) {
		// Update Message
		message = 'you bitch';
		$('#score').delay(100).text(0).css({'color':'red'}).fadeIn('slow');
		
		// Update Modal Pop-up
		$('#resetModal').modal('toggle')
		
		
		$('#missed').empty();
		$('#sets').empty();
		
		
		for (var i = 0; i < sets.length; i++) {
			var imgs = imageHandler(sets[i][0],sets[i][1],sets[i][2]);
			var missedStr = '<div>' + imgs + '</div><br>'
			$('#missed').append(missedStr);
		}
		data['resetScore'] = 1;
	}
	else {
		message = 'good call';
		}
	$('#message').text(message).css({'color':'red'});
	$('#message').delay(45).fadeIn('fast');

	
	setStart = Date.now();  // Reset Timer
	
	// Reset Board
	$.ajax({
	type: "get",
	url: "/reset",
	data: data,
	dataType: 'json',
	success: function(data) {
		// Un-highlight everything
		$('.highlight').removeClass('highlight');
		cards = data['board'];
		// Set new board
		for (var i = 0; i < 12; i++) {
			$('#tile'+i).attr('src','/static/imgs/'+pad(cards[i],2)+'.gif');
		}
	}
	});


}

// Take 3 images. Returns string of <img> tags
var imageHandler = function(img1,img2,img3) {
	var i1 = '/static/imgs/' + pad(img1,2);
	var i2 = '/static/imgs/' + pad(img2,2);
	var i3 = '/static/imgs/' + pad(img3,2);
	
	var imgs = '<img style=\'width:33%\' class=\'img-rounded\' src=\''+ i1 + '.gif\'></img>';
	imgs    += '<img style=\'width:33%\' class=\'img-rounded\' src=\''+ i2 + '.gif\'></img>';
	imgs    += '<img style=\'width:33%\' class=\'img-rounded\' src=\''+ i3 + '.gif\'></img>';
	
	return imgs;
}

var scoreClick = function() {

	// get current score and name
	var name = $('#username').val();
	
	if (!name) {
		$('#message').text('ugggh..');
		return 0;
	}
	
	var data = {'name':name};
	
	// put it on server if in top 25
	 $.ajax({
		 type: "POST",
		 url: "/set",
		 data: data,
		 dataType: 'json',
		 success: function(data) {
		 
			if (data['result']) {
				$('#message').text('so good!');
				$('#score').delay(100).text(0).css({'color':'green'}).fadeIn('slow');
			}
			else {
				$('#message').text('not good enough').css({'color':'red'}).fadeIn('slow');
			}
			// Either way, rebuild leaderboard
			buildLB(data);

		 }
	 });
}


var buildLB = function(data) {

	// Empty table body
	$('#leaderBody').empty();
	
	var lb = data['lb'];
	for (var i = 0; i < lb.length; i++) {
		var name = lb[i][0];
		name = $('<i></i>').text(name).html();
		var score = lb[i][1];
		var htmlStr = '<tr><td>' + name + '</td>' + '<td>' + score + '</td></tr>';
		console.log(htmlStr);
		$('#leaderboard > tbody:last').append(htmlStr);
	}

}

// Generates unique random numbers.
// Arr can be blank or pre-populated
// cnt is desired length of array
var generRand = function(arr,cnt) {

	while(arr.length < cnt){
	  var randomnumber = Math.ceil(Math.random()*81)
	  var found = false;
	  for(var i=0;i<arr.length;i++){
		if(arr[i]==randomnumber) {
			found=true;
			break 
		}
	  }
	  if(!found)
		arr[arr.length]=randomnumber;
	}
	return arr;

}

function pad(num, size) {
    var s = "0" + num;
    return s.substr(s.length-size);
}

var setCheck = function() {
	var sets = [];
	for (var i = 0; i < $('.tileImg').length; i++) {
		for (var j = i + 1; j < $('.tileImg').length; j++) {
			for (var k = j + 1; k < $('.tileImg').length; k++) {
			
			var tile1 = parseInt(String($('#tile'+i).attr('src').slice(13,15)));
			var tile2 = parseInt(String($('#tile'+j).attr('src').slice(13,15)));
			var tile3 = parseInt(String($('#tile'+k).attr('src').slice(13,15)));
			
			if (evaluate([tile1,tile2,tile3]))
				sets.push([tile1,tile2,tile3]);
			}
		}
	}
	return sets;
	
}

var evaluate = function(setAr) {
	var success = true;
	// evaluate fill
	if ((fill(setAr[0]) == fill(setAr[1]) && fill(setAr[1]) != fill(setAr[2])) ||
		(fill(setAr[0]) != fill(setAr[1]) && fill(setAr[1]) == fill(setAr[2])) ||
		(fill(setAr[0]) == fill(setAr[2]) && fill(setAr[0]) != fill(setAr[1])))
		{ success = false; }
	// evaluate qty
	if ((qty(setAr[0]) == qty(setAr[1]) && qty(setAr[1]) != qty(setAr[2])) ||
		(qty(setAr[0]) != qty(setAr[1]) && qty(setAr[1]) == qty(setAr[2])) ||
		(qty(setAr[0]) == qty(setAr[2]) && qty(setAr[0]) != qty(setAr[1])))
		{ success = false; }
	// evaluate shape
	if ((shape(setAr[0]) == shape(setAr[1]) && shape(setAr[1]) != shape(setAr[2])) ||
		(shape(setAr[0]) != shape(setAr[1]) && shape(setAr[1]) == shape(setAr[2])) ||
		(shape(setAr[0]) == shape(setAr[2]) && shape(setAr[0]) != shape(setAr[1])))
		{ success = false; }
	// evaluate color
	if ((color(setAr[0]) == color(setAr[1]) && color(setAr[1]) != color(setAr[2])) ||
		(color(setAr[0]) != color(setAr[1]) && color(setAr[1]) == color(setAr[2])) ||
		(color(setAr[0]) == color(setAr[2]) && color(setAr[0]) != color(setAr[1])))
		{ success = false; }
	return success;
}
// Notes on element values:
// N <= 27 = Solid
// N > 27 && <= 54 = Stripes
// N > 54 = Blank
// N % 3 == 1 = Qty 1
// N % 3 == 2 = Qty 2
// N % 3 == 0 = Qty 0
// N % 9 == 1,2,3 = Red
// N % 9 == 4,5,6 = Purple
// N % 9 == 7,8,0 = Green
// N % 27 == 1-9 = Squiggle
// N % 27 == 10-18 = Diamond
// N % 27 == 19-26,0 = Oval
var fill = function(val) {
	if (val <= 27)
		return 1; // Solid
	if (val <= 54)
		return 2; // Stripes
	return 3; // Blank
}
var qty = function(val) {
	if (val % 3 == 1)
		return 1;
	if (val % 3 == 2)
		return 2;
	return 3;
}
var shape = function(val) {
	val = val % 27;
	if (val >= 1 && val <= 9)
		return 1;
	if (val >= 10 && val <= 18)
		return 2;
	return 3;
}
var color = function(val) {
	val = val % 9
	if (val >= 1 && val <= 3)
		return 1
	if (val >= 4 && val <= 6)
		return 2
	return 3
}