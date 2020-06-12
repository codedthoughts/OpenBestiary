var fs = require('fs')
, ini = require('ini')
, util = require('util')
, os = require('os');

let name = process.argv[2];
var config = ini.parse(fs.readFileSync(os.homedir+'/.config/bestiary.nim/bestiary.'+name+'.ini', 'utf-8'));

fs.writeFile(os.homedir+'/.config/bestiary.nim/bestiary.'+name+'.json', util.inspect(config, {showHidden: false, depth: null}), function(err) {
    if(err) 
        console.log(err);
    else
		console.log("The file was saved!\n "+os.homedir+"/.config/bestiary.nim/bestiary."+name+".json");
	
	
}); 
