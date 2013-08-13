$(function(){
    
  /*
        Ismael Celis 2010
        Simplified WebSocket events dispatcher (no channels, no users)

        var socket = new ServerEventsDispatcher();

        // bind to server events
        socket.bind('some_event', function(data){
                alert(data.name + ' says: ' + data.message)
        });

        // broadcast events to all connected users
        socket.trigger( 'some_event', {name: 'ismael', message : 'Hello world'} );
  */
  var ServerEventsDispatcher = function( ){
        var loc = window.location, new_uri;
        if (loc.protocol === "https:") {
          new_uri = "wss:";
        } else {
          new_uri = "ws:";
        }
        new_uri += "//" + loc.host; //loc.pathname taken out
        new_uri += "/ws";
        var conn = new WebSocket(new_uri);
        var callbacks = {};

        this.bind = function(event_name, callback){
                callbacks[event_name] = callbacks[event_name] || [];
                callbacks[event_name].push(callback);
                return this;// chainable
        };

        this.trigger = function(event_name, data){
                var payload = JSON.stringify([event_name, data]);
                conn.send( payload ); // <= send JSON data to socket server
                return this;
        };

        // dispatch to the right handlers
        conn.onmessage = function(evt) {
                data = evt.data;

                if ( !data.charCodeAt(0) )
                        data = data.substr(1);

                var data = JSON.parse( data ),
                        event_name = data[0],
                        message = data[1];
                dispatch(event_name, message)
        };

        conn.onclose = function(){dispatch('close',null)}
        conn.onopen = function(){dispatch('open',null)}

        var dispatch = function(event_name, message){
                var chain = callbacks[event_name];
                if(typeof chain == 'undefined') $(event_name).html(message)/*return*/; // no callbacks for this event
                for(var i = 0; i < chain.length; i++){
                        chain[i]( message )
                }
        }
  };
  

  /*var server = new ServerEventsDispatcher();
  server.bind('matchUpdate', function(evt){
    $('.matchList').html(evt.data);
  });
  server.bind('leaderboard', function(evt){
    $('.leaderboard').html(evt.data);
  });

    $('.noWinner').click(function(){
  $.ajax({

    type: "GET",
    url: "pickwinner",
    async: false,
    data: "match="+$(this).attr('match')+"&team=" + $(this).attr('team'),
    success: function(data){
      alert(data);
      $(this).parent().parent().parent().fadeOut("slow");
      $(this).parent().parent().html(data);
      $(this).parent().fadeIn("slow");
    }
  });*/
  var server = new ServerEventsDispatcher();
    	server.bind('top10games', function(evt){
   		var table = document.getElementByID("top10gamestable");
   		var tbody = table.getElementsByTagName("tbody")[0];
   		var rows = tbody.getElementsByTagName("tr");

   		function populateRow(index, data )
   		{
   			var row = rows[index];
   			var cells = row.getElementsByTagName("td")
   			var awayTeamCell = cells[1];
   			var homeTeamCell = cells[3];
   			var strengthCell = cells[4];
   			$(awayTeamCell).html(data['away']);
   			$(homeTeamCell).html(data['home']);
   			$(strengthCell).html(data['strength']);

   		}
    		

   		for(i=0;i<evt.data.length;i++){
   			populateRow(i, evt.data['games'][i], True)
   		}
   		$("#working").html = evt.data['isdone']

  });
  		
  function recalculate() {
  			var form = document.getElementByID("names")
  			var names = form.getElementsByTagName("input")
  			server.trigger('gettop10games', names)
  }
  return false;
});