var http = require("http");
process.env.TZ = 'Europe/Moscow';
http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
setInterval(function () {
    let date_ob = new Date();
    let hourse = date_ob.getHours();
    console.log(hourse);
    available = [22,23,24,0,1,2,3,4,5,6,7,8].includes(hourse);
    if (!available) {
        console.log('send http requests');
        http.get("http://partnerweb3.herokuapp.com");
        http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
    }
}, 300000); // every 5 minutes