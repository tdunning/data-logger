import support

### Wake up, turn on WIFI
wakeWifi()

### scan all sensors and report values
reportTemps(readTemps())

### find out what to do next
config = getConfig()

### go into deep sleep or start web REPL
if config.get('sleep'):
    sleepTime = config['sleep']
    if sleepTime > 200:
        sleepTime = 200
    if sleepTime < 0:
        sleepTime = 5
    deepSleep(sleepTime)
else:
    repl()

