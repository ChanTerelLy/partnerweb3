# Partnerweb3
This is virlual CRM-system based on <https://partnerweb.beeline.ru>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ChanTerelLy/partnerweb3)

Deployed project versions:
- master-branch(all stable features) <https://partnerweb3.herokuapp.com> 
- master-dev(test server) <https://partnerweb3-test.herokuapp.com> 
- master-legacy(very old branch, only sync tickets load) <https://partnerweb3-legacy.herokuapp.com>

## Deployment

 Installation by docker-compose:
 - copy .env.default to .env
 - fill in credential
 - execute docker script
 ```shell script
$ docker-compose up -d --build
```

## Note to .env
- use postgres credential
- SELL_CODE is **required field**
- OPERATOR, PASS is not required
- CITIES_ID used in searching system
- NIGHT_TIME_BLACKOUT - disable autoping script at night
- BRANCH used for AWS static file prefix bucket

## Development notes
**TURN ON** 'no reload' option and gevent compatible in IDE when
 starting django server if you want to use debug.