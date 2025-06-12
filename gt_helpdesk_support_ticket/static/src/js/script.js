odoo.define('gt_helpdesk_support_ticket.script', function(require) {
    'use strict';



    var ajax = require('web.ajax');
    var tour = require('web_tour.tour');
    var base = require('web_editor.base');
    var website = require('website.website');
    var base = require('web_editor.base');

$(document).ready(function()
{
	// Variable to set the duration of the animation
	var animationTime = 500;
	
	// Variable to store the colours
	var colours = ["bd2c33", "e49420", "ecdb00", "3bad54", "1b7db9"];

	// Add rating information box after rating
	var ratingInfobox = $("<div />")
		.attr("id", "ratinginfo")
		.insertAfter($("#rating"));

	// Function to colorize the right ratings
	var colourizeRatings = function(nrOfRatings) {
		$("#rating li a").each(function() {
			if($(this).parent().index() <= nrOfRatings) {
				$(this).stop().animate({ backgroundColor : "#" + colours[nrOfRatings] } , animationTime);
			}
		});
	};
	
	// Handle the hover events
	$("#rating li a").hover(function() {
		
		// Empty the rating info box and fade in
		ratingInfobox
			.empty()
			.stop()
			.animate({ opacity : 1 }, animationTime);
		
		// Add the text to the rating info box
		$("<p />")
			.html($(this).html())
			.appendTo(ratingInfobox);
		
		// Call the colourize function with the given index
		colourizeRatings($(this).parent().index());
	}, function() {
		
		// Fade out the rating information box
		ratingInfobox
			.stop()
			.animate({ opacity : 0 }, animationTime);
		
		// Restore all the rating to their original colours
		$("#rating li a").stop().animate({ backgroundColor : "#333" } , animationTime);
	});
	
	// Prevent the click event and show the rating
	$("#rating li a").click(function(e) {
		e.preventDefault();
		alert("Thank you for giving us " + ($(this).parent().index() + 1)+" rates");
		var rate_val=($(this).parent().index() + 1)
		var rate_dis=$(this).text();
		var rc_id = document.getElementById("rc").value


		ajax.jsonRpc("/page/feedback_thanks", 'call', {
                    'rate': rate_val,
                    'rc_id': rc_id,
                    'rate_msg': rate_dis
                    }).then(function (event_name) {
            website.form('/page/helpdesk_tickets/');
//            website.form('/page/helpdesk_tickets/');
            });


	});
});


});
