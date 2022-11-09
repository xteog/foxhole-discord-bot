import requests
import json
import defs
from math import sqrt


def updateData(map, newData, opt):
  data = read(defs.DB['mapData'].format(map))

  if opt == 0:
    data['mapTextItems'] = newData
  elif opt == 1:
    data['mapItems'] = newData
  elif opt == 2:
    data = newData

  write(defs.DB['mapData'].format(map), data)

def downloadData(map, opt, etag='"-1"'):
  url = [defs.DB['staticData'], defs.DB['dynamicData']]
  data = [0, 0, 0]
    
  if map != 'MarbanHollow':
    map = map + 'Hex'

  if opt == 0:
    data = requests.get(url[0].format(map)).json()
  elif opt == 1:
    response = requests.get(url[1].format(map), headers={"If-None-Match": etag})
    if response.status_code == 200:
      data = response.json()
      data['ETag'] = response.headers['ETag']
    elif response.status_code == 304:
      data = None
  elif opt == 2:
    static = requests.get(url[0].format(map)).json()
    response = requests.get(url[1].format(map))
    dynamic = response.json()
    dynamic['ETag'] = response.headers['ETag']
    dynamic['mapTextItems'] = static['mapTextItems']
    data = dynamic

  return data

def updateMapL():
  url = 'https://war-service-live.foxholeservices.com/api/worldconquest/maps'
  response = requests.get(url)
  mapName = response.json()
  for i in range(len(mapName)):
    mapName[i] = mapName[i].split('Hex')[0]

  write(defs.DB['mapName'], mapName)

def setName(map):
  data = read(defs.DB['mapData'].format(map))
  for itemS in data['mapTextItems']:
    cont = 0.001
    cond = 1
    while(cond):
      for itemD in data['mapItems']:
        if itemD['flags'] == 8 or itemD['flags'] == 41:
          if itemS['mapMarkerType'] == 'Major':
            d = sqrt((itemD['x'] - itemS['x'])**2 + (itemD['y'] - itemS['y'])**2)

            if d < cont:
              cond = 0
              i = data['mapTextItems'].index(itemS)
              j = data['mapItems'].index(itemD)
              data['mapTextItems'][i]['location'] = j
              break
          else:
            cond = 0
            break
      cont = cont + 0.001
  updateData(map, data['mapTextItems'], 0)
  #print(data['mapText'])

def write(path, data):
  data = json.dumps(data, indent=2)
  with open(path, 'w') as f:
    f.write(data)
    
def read(path):
  with open(path, 'r') as f:
    file = f.read()
  return json.loads(file)
