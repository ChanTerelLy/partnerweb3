
var http = require("http");
setInterval(function() {
    http.get("http://partnerweb3.herokuapp.com");
    http.get("http://partnerweb3-test.herokuapp.com");
}, 300000); // every 5 minutes (300000)