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
import time

app = Flask(__name__)

data = dict()
names = dict()

@app.route('/start/<source>')
def register(source):
    data[source] = dict()
    return("Registered %s" % source)

@app.route('/data/<source>/<sensor>/<value>')
def sendSample(source, sensor, value):
    record(source, sensor, value, time.time())
    return("Received value for %s/%s %s" % (source, sensor, data))


@app.route('/data')
def getAll():
    return(str(filter(data, request.args)))

@app.route('/data/<source>')
def getSource(source):
    return(str(filter(data, request.args, source=source)))

@app.route('/data/<source>/<sensor>')
def getSensor(source, sensor):
    return(str(filter(data, request.args, source=source, sensor=sensor)))

@app.route('/csv')
def getCSV():
    r = []
    for s1 in data:
        for s2 in data[s1]:
            for (t,v) in data[s1][s2]:
                r.append("%s,%s,%s,%s" % (t,s1,s2,v))
    return("\n".join(r))

@app.route('/label/<source>/<sensor>')
def label(source, sensor):
    name = request.args.get('name')
    if name:
        recordLabel(source, sensor, name)
    return 'OK'
    
### TODO GET  /stream?query => retrieve data as a websockets

from datetime import datetime

def record(source, sensor, value, t, log=True):
    if log:
        with open("data.csv", "a") as f:
            f.write("%.3f,%s,%s,%s\n" % (t, source, sensor, value))
    if not source in data:
        data[source] = dict()
    if not sensor in data[source]:
        data[source][sensor] = []
    data[source][sensor].append((t, value))

def reloadData():
    with open("data.csv", "r") as f:
        for line in f:
            (time, source, sensor, value) = line.strip().split(',')
            record(source, sensor, float(value), float(time), log=False)
    with open("names.csv", "r") as f:
        for line in f:
            (time, source, sensor, name) = line.strip().split(',')
            names[(source, sensor)] = name

def interpretTimeParameter(t, default=0, now=time.time()):
    if t == None:
        t = default
    try:
        t = float(t)
    except TypeError:
        # ignore
    if isinstance(t, float):
        if t < 1e6 and t >= -1e6:
            t = now + t
    elif isinstance(t, str):
        t = datetime.fromisoformat(t).timestamp()
    return(t)
    
def parseQuery(query):
    now = time.time()
    start = interpretTimeParameter(query.get('start', -3600), now=now)
    end = interpretTimeParameter(query.get('end', 0), now=now)
    limit = int(query.get('limit', 10))
    return(start, end, limit)

def inRange(v, start, end):
    return v >= start and v <= end

def filter(data, query, source=None, sensor=None):
    (start, end, limit) = parseQuery(query)
    r = dict()
    for src in data:
        if source == None or source == src: 
            r1 = dict()
            for se in data[src]:
                if sensor == None or sensor == se:
                    samples = data[src][se]
                    v = [sample for sample in samples if inRange(sample[0], start, end)]
                    if limit < 0:
                        v = v[limit:]
                    else:
                        v = v[:limit]
                    if len(v) > 0:
                        r1[se] = v
            if len(r1) > 0:
                r[src] = r1
    return(r)

def recordLabel(source, sensor, name, log=True):
    if log:
        with open("names.csv", "a") as f:
            f.write("%.1f,%s,%s,%s\n" % (time.time(), source, sensor, name))
    names[(source, sensor)] = name
    
reloadData()

