
var http = require("http");
setInterval(function() {
    http.get("http://partnerweb3.herokuapp.com");
    http.get("http://partnerweb3-test.herokuapp.com");
    http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
}, 180000); // every 3 minutes