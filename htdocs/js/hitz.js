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
        new_uri += "//" + loc.host;
        new_uri += loc.pathname + "/ws";
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
  

  var server = new ServerEventsDispatcher();
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
  });
  return false;
});
function loadMatchTest(match, team) {
  $.ajax({
    type: "GET",
    url: "/pickwinner",
    data: "match="+match+"&team=" + team,
    success: function(data){
      
      $("#"+match).html(data);
      
      return false;
    }

  });
  $.ajax({
    type: "GET",
    url: "/embedLeaderboard",
    
    success: function(data){
      
      $("#leaderboard").html(data);
      
      return false;
    }

  });
  return false;
}
function loadMatch(index)
{
  var xmlhttp;
  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange=function()
  {
    if (xmlhttp.readyState==4 && xmlhttp.status==200)
      {
        alert(xmlhttp.responseText)
        document.getElementByID(index).innerHTML=xmlhttp.responseText;
      }
  }
  xmlhttp.open("GET",$(this).attr('data-url'),true);
  xmlhttp.send();
  return false;
}
    
});