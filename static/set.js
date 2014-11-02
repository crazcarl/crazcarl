
// Right now this is going to work in continuous mode
$(document).ready(function() {

	// get 12 random numbers
	var cards = []
	cards = generRand(cards,12);
	
	// display them!
	
	for (var i = 0; i < 12; i++) {
		$('#tile'+i).attr('src','/static/imgs/'+pad(cards[i],2)+'.gif');
	}
	

	// Code to run when tile clicked
	$('.tileImg').click(cellClick);

});


var cellClick = function() {
	
	// (un)highlight the cell
	$('#'+this.id).toggleClass('highlight');
	
	if ($('.highlight').length > 2) {
		
		// Get all three elements values and current tile #
		setAr = [];
		tileAr = [];
		$('.highlight').each(function() {
			var tempInt = parseInt(String($(this).attr('src').slice(13,15))); //TODO: update when using static images
			setAr.push(tempInt);
			tileAr.push($(this).id);
		});
		
	
		var success = evaluate(setAr);
		
		// Un-highlight everything
		$('.highlight').removeClass('highlight');
		
		if (success) {
			alert('yeah, buddy!');
			
			var newAr = [];
			// Get current list of cards being used
			$('.tileImg').each(function() {
				var tempInt = parseInt(String($(this).attr('src').slice(13,15)));
				newAr.push(tempInt);
			});
			
			console.log('Current list is: ');
			console.log(newAr);
			
			// Pick three new elements randomly from list and swap out with previous
			generRand(newAr,15);
			
			console.log('With new elements; ');
			console.log(newAr);
			console.log(setAr);
			
			var tile0 = newAr.indexOf(setAr[0]);
			console.log('tile0: '+ tile0);
			$('#tile'+tile0).attr('src','/static/imgs/'+pad(newAr[12],2)+'.gif');
			
			var tile1 = newAr.indexOf(setAr[1]);
			console.log('tile1: '+ tile1);
			$('#tile'+tile1).attr('src','/static/imgs/'+pad(newAr[13],2)+'.gif');
			
			var tile2 = newAr.indexOf(setAr[2]);
			console.log('tile2: '+ tile2);
			$('#tile'+tile2).attr('src','/static/imgs/'+pad(newAr[14],2)+'.gif');
			
			// Update score
		}
		else {
			alert('try harder');
		}
	}
};

var evaluate = function(setAr) {


	
	var success = true;
	
	// evaluate fill
	if ((fill(setAr[0]) == fill(setAr[1]) && fill(setAr[1]) != fill(setAr[2])) || 
	    (fill(setAr[0]) != fill(setAr[1]) && fill(setAr[1]) == fill(setAr[2])) ||
		(fill(setAr[0]) == fill(setAr[2]) && fill(setAr[0]) != fill(setAr[1])))
		{  console.log('fill fail');
		   success = false;        }
	
	// evaluate qty
	if ((qty(setAr[0]) == qty(setAr[1]) && qty(setAr[1]) != qty(setAr[2])) || 
	    (qty(setAr[0]) != qty(setAr[1]) && qty(setAr[1]) == qty(setAr[2])) || 
		(qty(setAr[0]) == qty(setAr[2]) && qty(setAr[0]) != qty(setAr[1])))
		{  console.log('qty fail');
		   success = false;        }
		
	// evaluate shape
	if ((shape(setAr[0]) == shape(setAr[1]) && shape(setAr[1]) != shape(setAr[2])) || 
	    (shape(setAr[0]) != shape(setAr[1]) && shape(setAr[1]) == shape(setAr[2])) ||
		(shape(setAr[0]) == shape(setAr[2]) && shape(setAr[0]) != shape(setAr[1])))
		{  console.log('shape fail');
		   success = false;        }

	// evaluate color
	if ((color(setAr[0]) == color(setAr[1]) && color(setAr[1]) != color(setAr[2])) || 
	    (color(setAr[0]) != color(setAr[1]) && color(setAr[1]) == color(setAr[2])) ||
		(color(setAr[0]) == color(setAr[2]) && color(setAr[0]) != color(setAr[1])))
		{  console.log('color fail');
		   success = false;        }
	
	
	return success;

}


// Notes on element values:
//  N <= 27           = Solid
//  N > 27 && <= 54   = Stripes
//  N > 54            = Blank
//  N % 3 == 1        = Qty 1
//  N % 3 == 2        = Qty 2
//  N % 3 == 0        = Qty 0
//  N % 9 == 1,2,3    = Red
//  N % 9 == 4,5,6    = Purple
//  N % 9 == 7,8,0    = Green
//  N % 27 == 1-9     = Squiggle
//  N % 27 == 10-18   = Diamond
//  N % 27 == 19-26,0 = Oval

var fill = function(val) {
	if (val <= 27)
		return 1;  // Solid
	if (val <= 54)
		return 2;  // Stripes
	return 3;	  // Blank
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
	if (val >= 10 &&  val <= 18)
		return 2;
	return 3;
}

var color = function(val) {
	val = val % 9
	if (val >= 1 && val <= 3)
		return 1
	if (val >= 4 &&  val <= 6)
		return 2
	return 3
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
	
	for (var i = 0; i < $('.tileImg').length; i++) {
		for (var j = i + 1; j < $('.tileImg').length; j++) {
			for (var k = j + 1; k < $('.tileImg').length; k++) {
			
			var tile1 = parseInt(String($('#tile'+i).attr('src').slice(13,15)));
			var tile2 = parseInt(String($('#tile'+j).attr('src').slice(13,15)));
			var tile3 = parseInt(String($('#tile'+k).attr('src').slice(13,15)));
			
			}
		}
	}
	
}