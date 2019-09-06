import json
"""
This server allows sensor data to be ingested and displayed

Each machine that has sensors should register. Data sent without registration will be dropped

Data can be interrogated in batch form or as a web-socket stream of updates

URLs include
POST /data/$source
POST /data/$source/$sensor?v=$value
GET  /data?$query  => list of sources, each with sensors and data
GET  /data/$source?$query => list of sensors from source, each with data 
GET  /data/$source/$sensor?query => get all data for a sensor
GET  /stream?query => retrieve data as a websockets
GET  /config?$source => retrieve configuration for this data source. Config is a json object that may contain a value for sleep.

The query here can involve the following parts:

limit - a positive value causes a specified number of data values to
        be retained from the beginning of the requested data. A
        negative value retains from the end. Default is -10

start - earliest time for with data should be returned. A small (<
        1e6) negative number indicates seconds prior to the present
        time. A large positive integer is taken as seconds since the
        epoch. Times can also be given in ISO 8601 format (YYYY-MM-DD
        or YYYY-MM-DDTHH:mm:ssZ). Default is -3600

end - latest time for which data should be returned. Formats accepted
        are as with start.  """

from flask import Flask
from flask import request
import support

app = Flask(__name__)

@app.route('/data/<source>/<sensor>/<value>')
def sendSample(source, sensor, value):
    record(source, sensor, value, time.time())
    return("Received value for %s/%s %s" % (source, sensor, data))

@app.route('/data')
def getAll():
    return(str(support.filter(request.args)))

@app.route('/data/<source>')
def getSource(source):
    return(str(support.filter(request.args, source=source)))

@app.route('/data/<source>/<sensor>')
def getSensor(source, sensor):
    return(str(support.filter(request.args, source=source, sensor=sensor)))

@app.route('/csv')
def getCSV():
    r = []
    r.append("time,source,sensor,value")
    filtered = support.filter(request.args)
    for s1 in filtered:
        for s2 in filtered[s1]:
            for (t,v) in filtered[s1][s2]:
                r.append("%s,%s,%s,%s" % (t,s1,s2,v))
    return("<pre>" + "\n".join(r) + "</pre>")

@app.route('/label/<source>/<sensor>')
def label(source, sensor):
    name = request.args.get('name')
    if name:
        recordLabel(source, sensor, name)
    return 'OK'

@app.route('/config/<source>')
def config(source):
    return json.dumps(support.getConfig(source))
    
### TODO GET  /stream?query => retrieve data as a websockets

    
support.reloadData()

