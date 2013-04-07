$(function(){
    
    $('.noWinner').click(function() {
        $.get( $(this).attr('data-url'), function(msg){
            $(this).html(msg['team']);    
        });
    });
    $('.lock').click(function(){
       $(this).html(oddClick[$(this).id] ? 'Unlock' : 'Lock');
       oddClick = !(oddClick); 
    });
	

});