

scrapyd-deploy tx2

curl http://111.230.148.143:3068/schedule.json -d project=sda -d spider=shangpin

scrapyd-deploy
scrapyd-deploy -l
scrapyd-deploy #-p seleniumcrawler
curl http://111.230.148.143:3068/schedule.json -d project=sda -d spider=yaopin
 curl http://111.230.148.143:3068/schedule.json -d project=sda -d spider=shangpin

curl http://111.230.148.143:3068/schedule.json -d project=sda -d spider=yaopin
curl http://111.230.148.143:3068/schedule.json -d project=sda -d spider=shangpin





curl http://111.230.148.143:3068/daemonstatus.json

curl http://111.230.148.143:3068/listprojects.json
curl http://111.230.148.143:3068/listversions.json?project=sda
curl http://111.230.148.143:3068/listjobs.json?project=sda
curl http://111.230.148.143:3068/listspiders.json?project=sda
curl http://111.230.148.143:3068/delproject.json -d project=sda
curl http://111.230.148.143:3068/cancel.json -d project=sda -d job=2c30657ef61211e7a99502420aff0009

