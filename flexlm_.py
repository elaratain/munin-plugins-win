# Reads number of available and used licences by flexlm license servers
# 
# Requirements:
#	- lmutil.exe
#
# Configuration:
#	- Rename to flexlm_LICENSEDAEMON.py
#	- Add variable to list:
#		LICENSEDAEMON = {"name": "DISPLAYNAME",
#		"lmstat": '"C:\\Path\\to\\lmutil.exe"',
#		"licfile": '"C:\\Path\\to\\licensefile"'
#		}
#	- you can add several LICENSEDAEMON lists and just create l;inks with the proper filename
#

import sys, re
import inspect, os, ntpath

if sys.platform == "win32":
	import os, msvcrt
	msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

SW_D = {"name": "Solidworks",
"lmstat": '"C:\\Program Files (x86)\\SOLIDWORKS SolidNetWork License Manager\\utils\\lmutil.exe"',
"licfile": '"C:\\Program Files (x86)\\SOLIDWORKS SolidNetWork License Manager\\licenses\\sw_d.lic"'
}

def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

def lmstat(name):
	from subprocess import check_output

	output = str(check_output(eval(name)["lmstat"] + " lmstat -c " + eval(name)["licfile"] + " -S " + name))
	match = output.find("Users of", 3)
	features = []
	while match != -1:
		matchFeatures = re.match("Users of ([^:]*):", output[match:])
		matchMax = re.match("[\w;: \(]*([\d]+) license[s]? issued", output[match+10:])
		matchUsers = re.match("[\w:; ]*([\d]+) license[s]? in use", output[match+35:])
		match = output.find("Users of", match+1)
		if matchFeatures is not None and matchUsers is not None and matchMax is not None:
			features.append({"name": matchFeatures.group(1), "users": matchUsers.group(1), "max": matchMax.group(1)})
		else:
			print("Features not found")
			exit
	return features

def config(name):
	features = lmstat(name)
	mx = 0
	for i in range(0, len(features)):
		mx = max(mx, int(features[i]["max"]))
	base_config = "graph_title FlexLM License usage for " + eval(name)["name"] + "\ngraph_args --base 1000 --vertical-label licenses -l 0 -u " + str(mx) + "\ngraph_category licensing\ngraph_period minute\n"
	for i in range(0, len(features)):
		base_config = base_config + features[i]["name"] + ".label " + features[i]["name"] + "\n"
		base_config = base_config + features[i]["name"] + ".draw LINE2\n"
		base_config = base_config + features[i]["name"] + ".info The number of " + features[i]["name"] + " licenses checked out\n"""
	sys.stdout.write(base_config + ".\n")

def fetch(name):
	features = lmstat(name)
	for i in range(0, len(features)):
		sys.stdout.write(features[i]["name"] + ".value " + features[i]["users"] + "\n")
	sys.stdout.write(".\n")

filename = path_leaf(inspect.stack()[0][1])
matchObj = re.match("flexlm_(.+)*.py", filename)
if matchObj:
	daemon = matchObj.group(1)
else:
	print("Unknown service name")
	exit

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] in ["autoconf", "detect"]:
			sys.stdout.write("yes")
		elif sys.argv[1] == "config":
			config(daemon)
		elif sys.argv[1] == "name":
			sys.stdout.write(eval(daemon)["name"])
		else:
			fetch(daemon)
	else:
		fetch(daemon)
