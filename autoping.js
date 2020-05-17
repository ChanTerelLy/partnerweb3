var http = require("http");
process.env.TZ = 'Europe/Moscow';
http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
setInterval(function () {
    let date_ob = new Date();
    let hours = date_ob.getHours();
    console.log(hours);
    if (!(hours > 21 && hours < 9)) {
        http.get("http://partnerweb3.herokuapp.com");
        http.get("http://partnerweb3-test.herokuapp.com");
        http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
    }
}, 300000); // every 5 minutes