################################################
#                                              #
#       Automated Map Generation Program       #
#           Multi-Mode .gif Module             #
#            Author: Sam Bailey                #
#        Last Revised: Mar 25, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################



#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def getFactors():
    return {}

def factors():
    return "Blank"

'''    
def multiMode():
    global Set
    global loaded
    levels = []
    
    print("<menu> Input commands, or type 'help'.")
    comm = input("<input> ")
    
    command = comm.split(" ")
    
    if command[0] == "help":
        for line in list(range(1, 58, 1)):
            print(manual[line], end='')
        multiMode()
    
    if command[0] == "list":
        print("<list> Type 'time' to set and print the current time.")
        print("<list> Type 'preset {name}' to load a map preset.")
        print("<list> Type 'preset list' to list available presets.")
        print("<list> Type 'edit {parameter}' to edit a given parameter.")
        print("<list> Type 'run' to run with the current settings.")
        print("<list> Type 'quit' to exit without running.")
        multiMode()
    
    
    if command[0] == 'time':
        getTime()
        multiMode()
#    elif command[0] == 'preset':
#        if command[1] == 'list':
#            keys = str(list(config['presets'].keys()))
#            print("<presets> Below is the list of all currently loaded presets:")
#            print("<presets> " + keys)
#            print("<presets> To edit or add presets, please switch back to individual mode.")
#            multiMode()
#        else:
#            presetLoad(command[1])
#            multiLoads()
#            multiMode()
    elif command[0] == 'edit':
        if command[1] in ['Date', 'DLoop', 'Jump', 'Delta', 'FCLoop', 'Levels']:
            if command[1] == 'Date':
                if command[2] == 'recent':
                    Set.update({'date':command[2]})
                elif command[2] == "today":
                    Set.update({'date':f'{command[2]}, {command[3]}'})
                else:
                    Set.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            elif command[1] == 'DLoop':
                Set.update({'dloop':command[2]})
            elif command[1] == 'Jump':
                Set.update({'jump':command[2]})
            elif command[1] == 'Delta':
                Set.update({'delta':command[2]})
            elif command[1] == 'FCLoop':
                Set.update({'fcloop':command[2]})
            elif command[1] == 'Levels':
                blankLevels = []
                count = 0
                if command[2] == "add":
                    blankLevels = Set['levels'].split(', ')
                    for item in command:
                        if count > 2:
                            blankLevels.append(command[count])
                        count += 1
                elif command[2] == "remove":
                    blankLevels = Set['levels'].split(', ')
                    for item in command:
                        if count > 2:
                            if command[count] in blankLevels:
                                blankLevels.pop(blankLevels.index(command[count]))
                            else:
                                print("<error> That is not a valid factor to remove!")
                                multiMode()
                        count += 1
                else:
                    for item in command:
                        if count > 1:
                            blankLevels.append(command[count])
                        count += 1
                Set.update({'levels':', '.join(blankLevels)})
        multiLoads()
        multiMode()
        
            
            
    elif command[0] == 'paste':
        multiLoads()
        multiMode()
    elif command[0] == 'run':
        save('prev')
        panels = []
        gif = False
        
        gifq = input("<run> Would you like to save these files as a .gif? [y/n]: ")
        if gifq == 'y':
            gif = True
        if gif:
            gifname = input("<run> What would you like to call this .gif?: ")
        date = Set['date']
        dloop = int(Set['dloop'])
        jump = int(Set['jump'])
        delta = int(Set['delta'])
        fcloop = int(Set['fcloop'])
        fchours = [delta]
        dates = [0]
        levels = Set['levels'].split(', ')
        
        while fcloop >= 1:
            fchours.append(delta + (fcloop * 6))
            fcloop = fcloop - 1
            
        while dloop >= 1:
            dates.append(dloop * jump)
            dloop = dloop - 1
        
        while dloop <= -1:
            dates.append(dloop * jump)
            dloop = dloop + 1
        
        overrides = {}
        for fch in fchours:
            for dt in dates:
                for lvl in levels:
                    overrides.update({'fcHour':fch,'level':lvl,'date':FromDatetime((ParseTime(date).time + timedelta(hours=dt))).ToString()})
                    product = run(loaded, '', **overrides)
                    if gif:
                        panels.append(product)
                        print("<run> Map panel created successfully")
                    else:
                        SaveMap(product, True, doAssign, '', True)
                        
        if gif:
            c = 0
            for panel in panels:
                SaveMap(panel, False, False, f'{c:03d}', True)
                #if c == 0:
                #    SaveMap(panel, False, False, f'{c:03d}c', True)
                c = c + 1
            frames = []
#            if np.sign(Set['dloop']) == -1:
#                for image in glob.glob("../Maps/Temp/*.png"):
#                    frames.append(Image.open(image))
#            else:
            for image in reversed(glob.glob("../Maps/Temp/*.png")):
                frames.append(Image.open(image))
            frame_one = frames[0]
            if doAssign:
                frame_one.save(f"../Maps/Assignment_Maps/{gifname}.gif", format="GIF", append_images=frames, save_all=True, duration=1500, loop=0)
            else:
                frame_one.save(f"../Maps/Test_Maps/{gifname}.gif", format="GIF", append_images=frames, save_all=True, duration=1500, loop=0)
            print("<run> Gif created successfully")
            ClearTemp()
            
        multiMode()
        
    elif command[0] == 'mode':
        global mode
        if command[1] == 'plot':
            mode = 0
            inputChain()
        elif command[1] == 'skewt':
            mode = 2
            stlpMode()
    elif command[0] == 'quit':
        ClearTemp()
        sys.exit("<quit> The process was terminated.")
    else:
        print("<error> That is not a valid command!")
        multiMode()
        '''