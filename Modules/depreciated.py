# Depreciated Quickrun arguments from AMGP v0.1.0, unlikely to be reimplimented.



'''
if len(sys.argv) > 1:
    noShow = False
    dosave = False
    assigned = False
    allLevels = False
    allevels = ["surface", 850, 500, 300, 200]
    levels = []
    fchours = [0]
    dates = [0]
    jump = 6
    overrides = {}
    overrides.update({"fcloop":0})
    overrides.update({"dloop":0})
    overrides.update({"fcHour":0})
    setTime()
    if sys.argv[1] == "--quickrun":
        presetLoad('default')
        overrides.update({"level":"surface"})
        basedate = ParseTime("recent", "surface").T
        quickRun = True
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--preset":
                presetLoad(f'{sys.argv[i + 1]}')
            if sys.argv[i] == "-s":
                dosave = True
            if sys.argv[i] == "-a":
                assigned = True
            if sys.argv[i] == "--fchour":
                overrides.update({"fcHour":f"{sys.argv[i + 1]}"})
            if sys.argv[i] == "--level":
                levels.append(sys.argv[i + 1].replace('"', '').split(', '))
            if sys.argv[i] == "-allevels":
                levels = allevels
            if sys.argv[i] == "--fcloop":
                overrides.update({"fcloop":int(sys.argv[i + 1])})
            if sys.argv[i] == "--dloop":
                overrides.update({"dloop":int(sys.argv[i + 1])})
            if sys.argv[i] == "--jump":
                jump = sys.argv[i + 1]
            if sys.argv[i] == "-ns":
                noShow = True
            if sys.argv[i] == "--date":
                basedate = ParseTime(sys.argv[i + 1], overrides['level']).T
            if sys.argv[i] == "--factors":
                overrides.update({"factors":sys.argv[i + 1].replace('"', '')})
            i += 1
        
        while overrides['fcloop'] >= 1:
            fchours.append(overrides['fcloop'] * 6)
            overrides.update({"fcloop":(overrides['fcloop'] - 1)})
            
        while overrides['dloop'] >= 1:
            dates.append(overrides['dloop'] * jump)
            overrides.update({"dloop":(overrides['dloop'] - 1)})
            
        while overrides['dloop'] <= 1:
            dates.append(overrides['dloop'] * jump)
            overrides.update({"dloop":(overrides['dloop'] + 1)})
        
        for fch in fchours:
            for dt in dates:
                for lvl in levels:
                    overrides.update({'fcHour':fch})
                    overrides.update({'level':lvl})
                    overrides.update({'date':FromDatetime((basedate + timedelta(hours=dt)), overrides['level'])})
                    run(loaded, '', **overrides)
                    
    elif sys.argv[1] == "-help":
        for line in list(range(60, 136, 1)):
            if line != 135:
                print(manual[line], end='')
            else:
                print(manual[line])
        '''