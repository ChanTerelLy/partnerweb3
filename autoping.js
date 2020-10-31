var http = require("http");
const dotenv = require('dotenv');
dotenv.config();
process.env.TZ = 'Europe/Moscow';
console.log('tickets_redis_json FIRE');
http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
setInterval(function () {
    let denied = false;
    if (parseInt(process.env.NIGHT_TIME_BLACKOUT)){
        let date_ob = new Date();
        let hourse = date_ob.getHours();
        console.log(hourse);
        denied = [22, 23, 24, 0, 1, 2, 3, 4, 5, 6, 7, 8].includes(hourse);
    }
    if (!parseInt(denied)) {
        console.log('send http requests');
        console.log('tickets_redis_json FIRE');
        http.get("http://partnerweb3.herokuapp.com");
        http.get("http://partnerweb3.herokuapp.com/tickets_redis_json/");
        if (parseInt(process.env.USE_CELERY)) {
            http.get("http://partnerweb3.herokuapp.com/firebase_notify_calls/"); //TODO: NIGHT BLACKOUT not working with celery
        }
    }
}, 300000); // every 5 minutes