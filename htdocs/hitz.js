$(function(){
    
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
	  var loc = window.location, new_uri;
    if (loc.protocol === "https:") {
      new_uri = "wss:";
    } else {
      new_uri = "ws:";
    }
    new_uri += "//" + loc.host;
    new_uri += loc.pathname + "/to/ws";
    var ws = new WebSocket(new_uri);
     ws.onopen = function()
     {
        // Web Socket is connected, send data using send()
        ws.send("Message to send");
        alert("Message is sent...");
     };
     ws.onmessage = function (evt) 
     { 
        var received_msg = evt.data;
        alert("Message is received...");
     };
     ws.onclose = function()
     { 
        // websocket is closed.
        alert("Connection is closed..."); 
     };
});