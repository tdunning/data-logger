import time
import json
import os
import os.path
from datetime import datetime

data = dict()
names = dict()
configValues = dict()
lastLoad = {}

def record(source, sensor, value, t, log=True):
    global data
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
    loadConfigs()

def loadConfigs():
    global configValues
    if os.path.getmtime("configs.json") > lastLoad.get('configs', 0):
        with open("configs.json", "r") as f:
            configValues = json.loads(f.read())
        lastLoad['configs'] = time.time()

def interpretTimeParameter(t, default=0, now=time.time()):
    if t == None:
        t = default
    try:
        t = float(t)
    except TypeError:
        # ignore
        t = t
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
    limit = int(query.get('limit', -200))
    return(start, end, limit)

def inRange(v, start, end):
    return v >= start and v <= end

def filter(query, source=None, sensor=None):
    global data
    (start, end, limit) = parseQuery(query)
    source = query.get('source', source)
    sensor = query.get('sensor', sensor)
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
                    elif limit > 0:
                        v = v[:limit]
                    if len(v) > 0:
                        r1[se] = v
            if len(r1) > 0:
                r[src] = r1
    return(r)

def recordLabel(source, sensor, name, log=True):
    global names
    if log:
        with open("names.csv", "a") as f:
            f.write("%.1f,%s,%s,%s\n" % (time.time(), source, sensor, name))
    names[(source, sensor)] = name

def getConfig(source):
    global configValues
    loadConfigs()
    return configValues.get(source, configValues.get('-'))
