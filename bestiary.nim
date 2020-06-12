import parsecfg, os, rdstdin, kaiser
import strutils, streams, rainbow
const VERSION = "0.1.6"
var
    cfg:Config
#[
iteration idea for Find
while hitting keys, keep adding the lines to a string builder
if any lines match, set a var true
when hitting section start or eof, check if var is true, if yes, send
reset string builder and var, then add section headr to new string builder

exporter to json
]#
proc load() =
    let g = getEnv("BESTIARY_GROUP")
    if g == "": return
    
    if not existsFile(getConfigDir()&"bestiary.nim/bestiary."&g&".ini"):
        cfg = newConfig()
    else:
        cfg = loadConfig(getConfigDir()&"bestiary.nim/bestiary."&g&".ini")
        
proc load(g:string) =
    putEnv("BESTIARY_GROUP", g)
    if not existsFile(getConfigDir()&"bestiary.nim/bestiary."&g&".ini"):
        cfg = newConfig()
    else:
        cfg = loadConfig(getConfigDir()&"bestiary.nim/bestiary."&g&".ini")
        
proc ls(group:string) = # maybe find a way to exclude the meta key
    putEnv("BESTIARY_GROUP", group)
    load(group)
    let path = getConfigDir()&"bestiary.nim/bestiary."&group&".ini"
    var f = newFileStream(path, fmRead)
    if f != nil:
        var p: CfgParser
        open(p, f, path)
        while true:
            var e = next(p)
            case e.kind
            of cfgEof: break
            of cfgSectionStart:
                echo("\n [ " & e.section.rfGreen & " ]")
            of cfgKeyValuePair:
                echo(e.key.rfBlue & ": " & e.value)
            of cfgOption:
                echo("command: " & e.key & ": " & e.value)
            of cfgError:
                echo(e.msg)
                close(p)
                
proc ls() =
    if getEnv("BESTIARY_GROUP") != "":
        getEnv("BESTIARY_GROUP").ls()
    else:
        echo "No default group to detect mob from."
        
proc addToBestiary(mob:string, group:string) =
    putEnv("BESTIARY_GROUP", group)
    load(group)
    cfg.setSectionKey(mob, "name", mob)
    cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
    echo "Mob "+mob+" created in "+group
    
proc addToBestiary(mob:string) =
    if getEnv("BESTIARY_GROUP") != "":
        mob.addToBestiary(getEnv("BESTIARY_GROUP"))
    else:
        echo "No default group to detect mob from."
        
proc modifyMobField(group, mob, field, value:string) =
    putEnv("BESTIARY_GROUP", group)
    load(group)
    echo "Mob "+mob+" in "+group+"'s field "+field+" is set to "+value
    cfg.setSectionKey(mob, field, value)
    
    cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
    
proc modifyMobField(mob, field, value:string) =
    if getEnv("BESTIARY_GROUP") != "":
        getEnv("BESTIARY_GROUP").modifyMobField(mob, field, value)
    else:
        echo "No default group to detect mob from."
        
proc main(input:var seq[string]) =
    let command = input.shift()

    case command:
        of "a", "add": # add <mob> [to <group>]
            if input.len == 1 and input[0] == "-h":
                echo "Adds a new mob."
                echo "Example: add <mob_name> [to <group>]"
                echo "$ add test character"
                echo "$ add test character 2 to others"
                return
                
            if input.len == 0:
                echo "No mob given..."
                return
                
            if input.len >= 3 and "to" in input:
                let mob = input.join(" ").split(" to ")[0]
                let group = input.join(" ").split(" to ")[1]
                echo "mob "+mob
                echo "grp "+group
                mob.addToBestiary(group)
            else:
                input.join(" ").addToBestiary
                
        of "new": # prompted input
            var g = getEnv("BESTIARY_GROUP")
            if input.len > 0:
                if input[0] == "-h":
                    echo "Prompts for input to create a new mob."
                    return
                g = input.join(" ")
                
            if g == "":
                g = readLineFromStdin("Group: ")
                if g == "":
                    echo "Cancelling."
            else:
                var i = readLineFromStdin("Group ["+g+"]: ")
                if i != "":
                    g = i
                    putEnv("BESTIARY_GROUP", g)
                    
            var name = readLineFromStdin("Name: ")
            #name.addToBestiary(g)

            echo "Input fields, in the format of `key = value`"
            echo "[Enter empty line to quit]"
            while true:
                var ln = readLineFromStdin(name+"> ")
                if ln == "":
                    break

                if ln.split(" ").len == 1:
                    modifyMobField(g, name, ln.split("=")[0].replace("_", " "), ln.split("=")[1].replace("_", " "))
                else:
                    modifyMobField(g, name, ln.split(" = ")[0].replace("_", " "), ln.split(" = ")[1].replace("_", " "))

        of "get": # [group.]keys
            if input.len == 1 and input[0] == "-h":
                echo "Gets a groups metadata."
                echo "Example: get [group.]key"
                return
            var group = ""
            var key = ""
            
            if "." in input[0]:
                group = input[0].split(".")[0]
                putEnv("BESTIARY_GROUP", group)
                key = input[0].split(".")[1]
            else:
                group = getEnv("BESTIARY_GROUP")
                key = input.join(" ")
                
            if group != "":
                load(group)
                echo cfg.getSectionValue(group+".meta", key)
                
        of "unset": # [group.]keys
            if input.len == 1 and input[0] == "-h":
                echo "Removes a groups metadata field."
                echo "Example: unset [group.]key"
                return
            var group = ""
            var key = ""
            
            if "." in input[0]:
                group = input[0].split(".")[0]
                putEnv("BESTIARY_GROUP", group)
                key = input[0].split(".")[1]
            else:
                group = getEnv("BESTIARY_GROUP")
                key = input.join(" ")
                
            if group != "":
                load(group)
                cfg.delSectionKey(group+".meta", key)
                cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
                
        of "set": # [group.]key = value
            if input.len == 0:
                echo "expected [group.]key = value"
                return
                
            if input.len == 1 and input[0] == "-h":
                echo "Modifies a groups metadata."
                echo "Example: set [group.]key = value"
                echo "$ set test.author = Kai"
                echo "$ set author = Me"
                return
                
            var group = getEnv("BESTIARY_GROUP")
            var key = ""
            var value = ""
            var ln = ""
            
            if input.len == 1: # [group.]key=value
                ln = input[0].split("=")[0]
                value = input[0].split("=")[1]
            else:
                ln = input.join(" ").split(" = ")[0]
                value = input.join(" ").split(" = ")[1]
                
            if "." in ln:
                group = ln.split(".")[0]
                putEnv("BESTIARY_GROUP", group)
                key = ln.split(".")[1]
            else:
                key = ln

            if group == "":
                echo "No group to apply to."
                return
                
            
            load(group)
            cfg.setSectionKey(group+".meta", key, value)
            cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
            echo "Meta variable "+group+"."+key+" set to "+value
            
        of "modify", "mod", "m": # [group.]mob.key = value
            if input.len == 1 and input[0] == "-h":
                echo "Modifies a groups metadata."
                echo "Example: modify [group.]mob.key = value"
                echo "$ mod test.Wasp.power = 5"
                echo "$ mod Spider.horrorFactor = 10000"
                echo ""
                echo "If no value is given, i.e. the equals sign is omitted, it enters a REPL loop."
                return
                
            var group = ""
            var mob = ""
            var key = ""
            var value = ""
            var istr = input.join(" ")

            if not istr.contains("="):
                if istr.count(".") == 1:
                    group = istr.split(".")[0]
                    mob = istr.split(".")[1]
                elif istr.count(".") == 0:
                    mob = istr
                    if getEnv("BESTIARY_GROUP", "") == "":
                        group = readLineFromStdin("Group: ")
                    else:
                        group = getEnv("BESTIARY_GROUP")
                        
                echo "Input fields, in the format of `key = value`"
                echo "[Enter empty line to quit]"
                while true:
                    var ln = readLineFromStdin(group+"."+mob+"> ")
                    if ln == "":
                        break

                    modifyMobField(group, mob, ln.split("=")[0].strip().replace("_", " "), ln.split("=")[1].strip().replace("_", " "))

            else:
                if istr.count(".") == 1: 
                    mob = istr.split("=")[0].split(".")[0].replace("_", " ")
                    key = istr.split("=")[0].split(".")[1].replace("_", " ")
                elif istr.count(".") == 2:
                    group = istr.split("=")[0].split(".")[0].replace("_", " ")
                    mob = istr.split("=")[0].split(".")[1].replace("_", " ")
                    key = istr.split("=")[0].split(".")[2].replace("_", " ")
                value = istr.split("=")[1].replace("_", " ")

                if group != "":
                    modifyMobField(group.strip(), mob.strip(), key.strip(), value.strip())
                else:
                    modifyMobField(mob.strip(), key.strip(), value.strip())

        of "list", "ls": # ls [group]
            if input.len == 1 and input[0] == "-h":
                echo "Lists mobs in a group."
                echo "Example: ls [group]"
                return
                
            if input.len == 0:
                ls()
            else:
                input.join(" ").ls()
                
        of "r", "rem", "remove":
            if input.len == 0:
                echo "No value."
                return
                
            if input.len == 1 and input[0] == "-h":
                echo "Delete mob field."
                echo "Example: rem [group.]mob.key"
                return

            if input.len > 1:
                echo "Obscure value..."
                return
                
            var group = ""
            var mob = ""
            var field = ""
            if input[0].count(".") == 1 and getEnv("BESTIARY_GROUP") != "":
                group = getEnv("BESTIARY_GROUP")
                load(group)
                mob = input[0].split(".")[0].replace("_", " ")
                field = input[0].split(".")[1].replace("_", " ")
                cfg.delSectionKey(mob, field)
                cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
                echo "Removed field "+field+" from "+group+"."+mob
            elif input[0].count(".") == 2:
                putEnv("BESTIARY_GROUP", input[0].split(".")[0])
                group = input[0].split(".")[0]
                load(group)
                mob = input[0].split(".")[1].replace("_", " ")
                field = input[0].split(".")[2].replace("_", " ")
                cfg.delSectionKey(mob, field)
                cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
                echo "Removed field "+field+" from "+group+"."+mob
            
        of "d", "del", "delete":
            if input.len == 0:
                echo "No value."
                return
                
            if input.len == 1 and input[0] == "-h":
                echo "Delete mob."
                echo "Example: del [group.]mob"
                return

            if input.len > 1:
                echo "Obscure value..."
                return
                
            var group = ""
            
            if input[0].count(".") == 0 and getEnv("BESTIARY_GROUP") != "":
                group = getEnv("BESTIARY_GROUP")
                load(group)
                cfg.delSection(input[0].replace("_", " "))
                cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
                echo "Deleted mob "+group+"."+input[0].replace("_", " ")
            elif input[0].count(".") == 1:
                group = input[0].split(".")[0]
                putEnv("BESTIARY_GROUP", group)
                load(group)
                cfg.delSection(input[0].split(".")[1].replace("_", " "))
                cfg.writeConfig(getConfigDir()&"bestiary.nim/bestiary."&group&".ini")
                echo "Deleted mob "+group+"."+input[0].split(".")[1].replace("_", " ")
        of "groups":
            for kind, dir in walkDir(getConfigDir()&"bestiary.nim/"):
                if dir.endsWith(".ini"):
                    echo dir.split("bestiary.nim/")[1].split(".")[1]
        of "purge":
            if input.len == 0:
                echo "missing group name."
            else:
                discard execShellCmd("rm "&getConfigDir()&"bestiary.nim/bestiary."&input[0]&".ini")
        of "show":
            echo "Showing mob by name"
        of "find":
            echo "Finding mobs with matching field"
        of "edit":
            if input.len == 0:
                echo "missing group name."
            else:
                let cmd = getEnv("BESTIARY_EDIT_COMMAND", "xdg-open")
                discard execShellCmd(cmd&" "&getConfigDir()&"bestiary.nim/bestiary."&input[0]&".ini")
        of "help", "h":
            echo "Bestiary "+VERSION
            echo ""
            echo "A way of sorting and saving mob data in a digital bestiary, supporting groups and arbitrary fields"
            echo ""
            echo "set - Sets metadata for group."
            echo "unset - Removes metadata field."
            echo "get - Gets metadata for group."
            echo "add - Creates new mob with a name field."
            echo "new - Prompt entry addition"
            echo "show - Shows mob with matching name"
            echo "find - Finds mob based on matching fields"
            echo "mod - Modifies field (will create mob and group if either doesn't exist)"
            echo "del - Deletes mob"
            echo "groups - Lists groups"
            echo "purge - Deletes group"
            echo "edit - Opens group in text editor, suggested by BESTIARY_EDIT_COMMAND environment."
            echo ""
            echo " * Use command with -h flag to show help for that command."
            echo " * If a command accepts a group property, it can usually be oitted, and the program will try to find the last used groupif in shell mode. (Note: May not always reliable, uses environment variable BESTIARY_GROUP)"
            echo " * For adding spaces in to names and fields, use underscore instead. (Makes it easier for the parsing system.)"
            echo ""
            echo "Using directory: "+getConfigDir()+"bestiary.nim/"
            echo "ENV_VARS: "
            echo "BESTIARY_GROUP = "+getEnv("BESTIARY_GROUP", "NULL")
            echo "BESTIARY_EDIT_COMMAND = "+getEnv("BESTIARY_EDIT_COMMAND", "xdg-open")
        of "version", "v":
            echo VERSION
        of "exit", "quit":
            system.quit()
            
if not existsDir(getConfigDir()&"bestiary.nim/"):
    createDir(getConfigDir()&"bestiary.nim/")

if commandLineParams().len == 0:
    while true:
        var i = readLineFromStdin("> ").split()
        if i[0] == ".q":
            system.quit()
        if i.len > 0:
            i.main()
        else:
            echo "Input a command..."
else:
    var arr = commandLineParams()
    main(arr)
