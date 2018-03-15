import sys
import os
import json

jsfile = 'test.js'
astfile = jsfile + '_ast.json'
os.system("js24 -e \"print(JSON.stringify(Reflect.parse(read('"+jsfile+"'))));\" > "+astfile)
