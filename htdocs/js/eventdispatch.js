
    
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
  var ServerEventsDispatcher = function(triggers ){
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
        var myself = this;

        this.bind = function(event_name, callback){
                callbacks[event_name] = callbacks[event_name] || [];
                callbacks[event_name].push(callback);
                return this;// chainable
        };

        this.trigger = function(event_name, data){
                var payload = JSON.stringify({'event':event_name, 'data':data});
                console.log(payload)
                conn.send( payload ); // <= send JSON data to socket server
                return this;
        };

        // dispatch to the right handlers
        conn.onmessage = function(evt) {
                data = evt.data;
                console.log(data);
                if ( !data.charCodeAt(0) ){
                        console.log(data.charCodeAt(0));
                        console.log(data.substr(1));
                        data = data.substr(1);
                      }

                var data = JSON.parse( data ),
                        event_name = data['event'];
                        console.log(data['event']);
                        message = data['data'];
                        console.log(data['data']);
                dispatch(event_name, message)
                console.log(event_name);
        };

        conn.onclose = function(){dispatch('close',null)}
        conn.onopen = function(){
          dispatch('open',null);
          console.log('websocket open');
          for (var h=0;h<triggers.length;h++){
            myself.trigger('subscribe', triggers[h])
          }
        }

        var dispatch = function(event_name, message){
                var chain = callbacks[event_name];
                console.log(event_name);
                if(typeof chain == 'undefined') return; // no callbacks for this event
                for(var i = 0; i < chain.length; i++){
                        chain[i]( message );
                }
                
        }
  }
  

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