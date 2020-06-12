#[ https://github.com/smallfx/luna.nim ]#
import json, httpclient, q, xmltree, os
import parseopt

proc `+`*(first, second:string):string =
    result = first & second
    
proc `-`*(a: var seq[any], second:any) =
    for i, v in a:
        if v == second:
            a.delete(i)
            break
        
proc shift*(a:var seq[any]):any=
    result = a[0]
    a.delete(0)

proc copy*(a:seq[string]):seq[string]=
    for en in a:
        result.add(en)
        
proc unshift*(a:var seq[any], newentry:any)=
    let old = a
    a = @[newentry]
    for en in old:
        a.add(en)
    
proc toStrArray*(js:seq[JsonNode]):seq[string]=
    for entry in js:
        result.add(entry.getStr)
        
proc toStrArray*(js:JsonNode):seq[string]=
    for entry in js.getElems():
        result.add(entry.getStr)
                
proc parseArgTable*():JsonNode =
    var p = initOptParser()
    var args = %*{}
    args[":args"] = newJArray()          
    while true:
        p.next()
        case p.kind
        of cmdEnd: break
        of cmdShortOption, cmdLongOption:
            if p.val == "":
                args[p.key] = newJBool(true)
            else:
                args[p.key] = newJString(p.val)
        of cmdArgument:
            args[":args"].add(newJString(p.key))
            
    return args
    
proc randomDog*(): string =
    let client = newHttpClient()
    let html = parseJson(client.getContent("https://random.dog/woof.json"))
    return html["url"].getStr
    
proc randomShibe*(): string =
    let client = newHttpClient()
    let html = parseJson(client.getContent("http://shibe.online/api/shibes?count=1&urls=true"))
    return html[0].getStr
    
proc randomBird*(): string =
    let client = newHttpClient()
    let html = parseJson(client.getContent("http://shibe.online/api/birds?count=1&urls=true"))
    return html[0].getStr
       
proc randomCat*(): string =
    let client = newHttpClient()
    let html = parseJson(client.getContent("http://aws.random.cat/meow"))
    return html["file"].getStr
    
proc randomBun*(): string =
    result = "https://dotbun.com/"
    let client = newHttpClient()
    result.add(q(client.getContent("https://dotbun.com/")).select("img")[1].attr("src"))
    
proc randomFox*(): string =
    let client = newHttpClient()
    let html = parseJson(client.getContent("https://randomfox.ca/floof/"))
    return html["image"].getStr
    
proc fopen*(url: string): int =
    var cmd = "xdg-open "
    cmd.add(url)
    result = execShellCmd(cmd)
    #err = exec.Command("xdg-open", url).Start() #RUN

    # WIN: "rundll32", "url.dll,FileProtocolHandler {url}"
    # WIN: "rundll32", "start {url}"
    # DARWIN: "open {url}"
