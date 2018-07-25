import sys
import requests
import json
from pandas.io.json import json_normalize


# This script is used to find and clean a map full of tasks using the wrike api
# first, a user is asked for the map name after which the program initializes the process.

print("please enter the exact name of the map")
filename = input()
print("The chosen file name is: " + filename)
# Find filename in wrike db and pull correct projectID
url = "https://app-eu.wrike.com/api/v3/folders?project=false&deleted=false"
with open("authorization.txt","r") as f:
    headers['authorization'] = f.read()
print(headers)

response = requests.get(url, headers=headers)
yields = str(response.text)
yields = yields.replace('☎', 'tel')

with open('wriketemp.json', 'w+') as outf:
    outf.write(yields)
with open('wriketemp.json') as f:
    result = json.load(f)
mapdictionary= {}
for i in range(len(result["data"])):
    mapdictionary[result["data"][i]["title"]] = result["data"][i]["id"]
try:
    mapID = mapdictionary[filename]
except(KeyError):
    print("Map name invalid, try again:")
    filename = input()
# Callback to issue command again
# Now that we know the mapId we can pull all tasks from said map:
url = "https://app-eu.wrike.com/api/v3/folders/"+mapID+"/tasks?descendants=true&pageSize=1000&fields=['customFields','authorIds']"
response = requests.get(url, headers=headers)
with open(filename+".json", 'w+') as outf:
    outf.write(response.text)
with open(filename+".json") as f:
    data = json.load(f)
usernamedict = {}
customfieldsdict = {}
for y in range(len(data["data"])):
    for i in data["data"][y]["customFields"]:
        cf = i['id']
        if cf in customfieldsdict.keys():
            i['id'] = customfieldsdict[cf]
        else:
            print("customFieldID not present, calling API")
            url = "https://app-eu.wrike.com/api/v3/customfields/" + cf
            response = requests.get(url, headers=headers)
            with open('wriketemp.json', 'w+') as outf:
                outf.write(response.text)
            try:
                with open('wriketemp.json') as f:
                    result = json.load(f)
            except:
                print("unexpected error")
            cfname = result["data"][0]["title"]
            customfieldsdict[cf] = cfname
            i['id'] = cfname

for i in data["data"]:
    users = i["authorIds"][0]
    if users in usernamedict.keys():
        i["authorIds"][0] = usernamedict[users]
    else:
        print("UserID not present, calling API")
        url = "https://app-eu.wrike.com/api/v3/users/" + users
        response = requests.get(url, headers=headers)
        with open('wriketemp.json', 'w+') as outf:
            outf.write(response.text)
        try:
            with open('wriketemp.json') as f:
                result = json.load(f)
        except:
            print("unexpected error")
        name = result["data"][0]["firstName"] + " " + result["data"][0]["lastName"]
        usernamedict[users] = name
        i["authorIds"][0] = name

with open(filename+".json", 'w+') as outfile:
    json.dump(data, outfile)




