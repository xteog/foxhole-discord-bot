import math
from multiprocessing import Event
import traceback
import discord
from discord import app_commands
from testRequest import updateData, downloadData, updateMapL, read, setName, write, updt_database, get_database
from testImage import updateMap, addCircle, changeColor
import testImage
import testImage
import time
import defs
from PIL import Image
import classes
import asyncio
import json
import datetime


class MyClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.server = defs.DB['serverId']
    self.day = datetime.datetime.utcnow().day #+1
    self.errorChannel = None
    self.depotChannel = None
    self.eventChannel = None
    self.dbChannel = None


  async def setup_hook(self) -> None:
    self.bg_task = self.loop.create_task(self.background_task())


  async def on_ready(self):
    await tree.sync(guild = discord.Object(id=self.server))
    
    self.errorChannel = self.get_channel(defs.DB['errorChannel'])
    self.depotChannel = self.get_channel(defs.DB['depotChannel'])
    self.eventChannel = self.get_channel(defs.DB['eventChannel'])
    self.dbChannel = self.get_channel(defs.DB['dataBaseChannel'])
    self.bollettinoChannel = self.get_channel(defs.DB['bollettinoChannel'])
    
    db = await get_database(self)
    str = 'Regioni di interesse:\n' + db['map_filter'][0]
    for i in range(1, len(db['map_filter'])):
      str += ', ' + db['map_filter'][i]
    await updt_database(db, self)
    await self.eventChannel.edit(topic=str)

    if len(db['depots']) > 0:
      embed, view = classes.view_depots(db['depots'][0]['group'], db['depots'])
      client.add_view(view)

    await client.change_presence(status=discord.Status.online)
    print('We have logged in as {}'.format(self.user.name))
    '''
  async def on_error(self):
    print('Error')
    await self.errorChannel.send(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n')
  '''


  async def background_task(self):
    await self.wait_until_ready()
    await asyncio.sleep(30)

    print('Background task started')
    while not self.is_closed():
      try:
        #await send_bollettino()
        mapName = await get_database(self)
        mapName = mapName['map_filter']
        str = 'Regioni di interesse:\n' + mapName[0]
        for i in range(1, len(mapName)):
          str += ', ' + mapName[i]
        #await self.eventChannel.edit(topic=str)

        #check_nukes()

        for map in mapName:
          list = []
          oldData = read(defs.DB['mapData'].format(map))
          newData = downloadData(map, 1, oldData['ETag'])
          
          if newData != None:
            updateData(map, newData, 2)
            data = await get_database(self)
            data['download'] += 1
            await updt_database(data, self)
            l = len(oldData['mapItems'])
            for i in range(l):
              j = search_item(oldData['mapItems'][i], newData['mapItems'])
              flag = convert_to_bin(newData['mapItems'][j]['flags'])
              if newData['mapItems'][j]['teamId'] != oldData['mapItems'][i]['teamId'] and flag[3] != '1':
                list.append((i, j))

          if len(list) > 0:
            data = newData
            data['mapTextItems'] = oldData['mapTextItems']
            newData = newData['mapItems']
            oldData = oldData['mapItems']
            
            updateMap(map, data, -1)
            setName(map)
            faction = search_faction(newData)
            #TODO vanno aggioranti le locations prima di switch


          for i, j in list:
            if newData[j]['iconType'] in defs.DB['iconFilter']:

              addCircle(map, (newData[j]['x'], newData[j]['y']))
              icon = defs.ICON_ID[newData[j]['iconType']]
              
              flag = convert_to_bin(newData[j]['flags'])
              if i == -1:
                message, color = await switch(map, newData[j]['teamId'], 'NONE', j, flag)
              elif j == -1:
                message, color = await switch(map, 'NONE', oldData[i]['teamId'], j, flag)
              else:
                message, color = await switch(map, newData[j]['teamId'], oldData[i]['teamId'], j, flag)
              
              description = icon + message
              embed=discord.Embed(title=description, color=color)
              
              if newData[j]['teamId'] == 'COLONIALS':
                color = 1
                if flag[1] == '1':
                  color = 2
                changeColor(Image.open(defs.DB['iconImage'].format(icon)), color).save(defs.PATH + '/data/tempIcon.png')
                fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
                embed.set_image(url='attachment://tempIcon.png'.format(icon))
              elif newData[j]['teamId'] == 'WARDENS':
                color = 0
                if flag[1] == '1':
                  color = 2
                changeColor(Image.open(defs.DB['iconImage'].format(icon)), color).save(defs.PATH + '/data/tempIcon.png')
                fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
                embed.set_image(url='attachment://tempIcon.png'.format(icon))
              else:
                if flag[1] == '1':
                  changeColor(Image.open(defs.DB['iconImage'].format(icon)), 2).save(defs.PATH + '/data/tempIcon.png')
                fileIcon = discord.File(defs.DB['iconImage'].format(icon))
                embed.set_image(url='attachment://{}.png'.format(icon))
              fileMap = discord.File(defs.PATH + '/data/tempImage.png')
              
              embed.set_thumbnail(url='attachment://tempImage.png')

              if faction == None:
                embed.set_author(name=map)
                files = [fileMap, fileIcon]
              else:
                fileFaction = discord.File(defs.DB['iconImage'].format(faction))
                embed.set_author(name=map, icon_url='attachment://{}.png'.format(faction))
                files = [fileMap, fileIcon, fileFaction]

              d, h, m = timeWar(data['lastUpdated'])
              embed.set_footer(text = f'{d}d {h}h {m}m')

              await client.eventChannel.send(files = files, embed=embed)

          await asyncio.sleep(1)
      except:
        print(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')
        await client.errorChannel.send(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')
      await asyncio.sleep(10)


  async def on_message(self, message):
    global presenze
    if message.author == client.user:
      presenze = message

    msg = message.content


def convert_to_bin(n):
  b = bin(n).replace('0b', '')[::-1]
  b += '0' * (6 - len(b))
  b = b[::-1]
  return b


def updt():
  #updateMapL()
  mapName = defs.MAP_NAME

  for map in mapName:
    newData = downloadData(map, 2)
    updateData(map, newData, 2)
    setName(map)
  print("Data updated")

  for map in mapName:
    data = read(defs.DB['mapData'].format(map))
    updateMap(map, data, -1)
  testImage.create_fullmap(defs.PATH + '/Map/Map{}.png')
  print("Maps updated")

  #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']


async def switch(map, newTeam, oldTeam, index, flag):
  collie = 0x65875E
  warden = 0x2D6CA1
  message = ''
  data = read(defs.DB['mapData'].format(map))

  for item in data['mapTextItems']:
    if item['mapMarkerType'] == 'Major' and item['location'] == index:
      message = item['text']
  
  if data['mapItems'][index]['iconType'] == 37:
    type = 1
  elif data['mapItems'][index]['iconType'] in (59, 60):
    type = 2
  else:
    type = 0
  
  message = ' di ' + message + '{}'
  msg = [message, message]
  if flag[5] == '1' and newTeam != 'NONE':
    msg[0] = message + '\nLa regione {} è stata persa!'.format(map)
    msg[1] = message + '\nLa regione {} è stata conquistata!'.format(map)

  try:
    if type == 0:
      if newTeam == 'NONE':
        if flag != '1':
          if oldTeam == 'COLONIALS':
            return msg[0].format(' è stato distrutto dai Wardens'), warden
          else:
            return msg[1].format(' è stato distrutto dai Colonials'), collie
        else:
          if oldTeam == 'COLONIALS':
            return msg[0].format(' è stato distrutto da una nuke dei Wardens'), warden
          else:
            return msg[1].format(' è stato distrutto da una nuke dei Colonials'), collie
      else:
        if newTeam == 'COLONIALS':
          return msg[1].format(' è stato conquistato dai Colonials'), collie
        else:
          return msg[0].format(' è stato conquistato dai Wardens'), warden
    elif type == 1:
      print()
    elif type == 2:
      if newTeam == 'NONE':
        if flag != '1':
          if oldTeam == 'COLONIALS':
            return msg[0].format(' è stato distrutto dai Wardens'), warden
          else:
            return msg[1].format(' è stato distrutto dai Colonials'), collie
        else:
          if oldTeam == 'COLONIALS':
            return msg[0].format(' è stato distrutto da una nuke dei Wardens'), warden
          else:
            return msg[1].format(' è stato distrutto da una nuke dei Colonials'), collie
      else:
        if newTeam == 'COLONIALS':
          return msg[1].format(' è stato costruito dai Colonials'), collie
        else:
          return msg[0].format(' è stato costruito dai Wardens'), warden


    if flag[1] != '1':


      if newTeam == 'NONE':
        if oldTeam == 'COLONIALS':
          return msg[0].format(' è stato distrutto dai Wardens'), warden
        else:
          return msg[1].format(' è stato distrutto dai Colonials'), collie
      else:
        if newTeam == 'COLONIALS':
          return msg[1].format(' è stato conquistato dai Colonials'), collie
        else:
          return msg[0].format(' è stato conquistato dai Wardens'), warden
    else:
      if nuke:
        if newTeam == 'COLONIALS':
          return msg[1].format(' è stata armata'), collie
        else:
          return msg[0].format(' è stata armata'), warden
      else:
        if oldTeam == 'COLONIALS':
          return msg[0].format(' è stato distrutto da un nuke!'), collie
        else:
          return msg[1].format(' è stato distrutto da un nuke!'), warden
  except:
    print(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')
    await client.errorChannel.send(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')


def timeWar(end):
  start = defs.DB['startWar']
  d = (end - start) / 86400000
  h = (d - int(d)) * 24
  m = (h - int(h)) * 60
  return int(d), int(h), int(m)

'''
def check_nukes():
  for map in defs.MAP_NAME:
    oldData = read(defs.DB['mapData'].format(map))
    if newData != None:
      updateData(map, newData, 2)
      data = await get_database()
      data['download'] += 1
      await updt_database(data, self)
      l = len(oldData['mapItems'])
      for i in range(l):
        j = search_item(oldData['mapItems'][i], newData['mapItems'])
        flag = convert_to_bin(newData['mapItems'][j]['flags'])
        if newData['mapItems'][j]['teamId'] != oldData['mapItems'][i]['teamId'] and flag[3] != '1':
          list.append((i, j))

    if len(list) > 0:
      data = newData
      data['mapTextItems'] = oldData['mapTextItems']
      newData = newData['mapItems']
      oldData = oldData['mapItems']
      
      updateMap(map, data, -1)
      setName(map)
      faction = search_faction(newData)
      #TODO vanno aggioranti le locations prima di switch
'''

def search_item(item, data):
  l = len(data)
  found = -1
  for i in range(l):
    if item['x'] == data[i]['x'] and item['y'] == data[i]['y']:
      found = i
  return found


def search_faction(data):
  found = -1
  for i in range(len(data)):
    flag = convert_to_bin(data[i]['flags'])
    if flag[5] == '1':
      found = i
  
  if found != -1:
    if data[found]['teamId'] == 'COLONIALS':
      str = 'ColonialFaction'
    elif data[found]['teamId'] == 'WARDENS':
      str = 'WardenFaction'
    else:
      return None
  else:
    return None
  return str
    

def loading(i, len):
  j = 0
  str = '|'
  perc = round(i/len*20, 1)
  while(j < 20):
    if perc > j:
      str += '█'
    else:
      str += '   '
    j += 1
  str += f'| {round(i/len*100, 1)}%'
  return str


def lev_dist(s, t):

    v0 = [i for i in range(len(t)+1)]
    v1 = [0]*(len(t)+1)

    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            deletionCost = v0[j + 1] + 1
            insertionCost = v1[j] + 1
            if s[i] == t[j]:
              substitutionCost = v0[j]
            else:
              substitutionCost = v0[j] + 1

            v1[j + 1] = min(deletionCost, insertionCost, substitutionCost)

        temp = v0
        v0 = v1
        v1 = temp
    return v0[-1]

list = []
for map in defs.MAP_NAME:
    data = read(defs.DB['mapData'].format(map))
    for i in range(len(data['mapItems'])):
      if data['mapItems'][i]['iconType'] in [33, 52]:
        min = 0
        index = -1
        for j in range(len(data['mapTextItems'])):
          if data['mapTextItems'][j]['mapMarkerType'] == 'Major':
            d = math.sqrt((data['mapItems'][i]['x'] - data['mapTextItems'][j]['x']) ** 2 + (data['mapItems'][i]['y'] - data['mapTextItems'][j]['y']) ** 2)
            if min > d or index == -1:
              min = d
              index = j
        if index != -1:
          icon = data['mapItems'][i]['iconType']
          list.append([data['mapTextItems'][index]['text'], map, 0, icon, (data['mapItems'][i]['x'], data['mapItems'][i]['y'])])
del min


async def location_autocomplete(interaction: discord.Interaction, current: str):
  for i in range(len(list)):
    list[i][2] = lev_dist(current.lower(), list[i][0][0:min(len(current), len(list[i][0]))].lower())
  
  list_f = []
  for i in range(5):
    minimum = 0
    for j in range(len(list)):
      if list[minimum][2] > list[j][2]:
        minimum = j
    list[minimum][2] = 100
    list_f.append(app_commands.Choice(name=f"{list[minimum][0]} ({defs.ICON_ID[list[minimum][3]]})", value=json.dumps(list[minimum])))
  return list_f


async def get_depot(interaction: discord.Interaction, current: str):
  l = []
  data = await get_database(client)
  for i in range(len(data['depots'])):
    l.append(app_commands.Choice(name=f"{data['depots'][i]['name']} a {data['depots'][i]['location']}({data['depots'][i]['map']})", value=i))
  return l


async def deletemessage(id):
    msg = await client.dbChannel.fetch_message(id)
    await msg.delete()


async def send_bollettino():
  testImage.create_fullmap(defs.DB['mapImage'])
  items = []
  for map in defs.MAP_NAME:
    items.append({'map': map})
  testImage.paste_text_fullmap(items)
  testImage.resize_fullmap()

  now = datetime.datetime.utcnow()
  if now.day >= client.day and now.hour >= 7:
    bol = classes.Bollettino()
    await client.bollettinoChannel.send(embed=bol, file=bol.fileMap)
    client.day += 1
  testImage.create_fullmap(defs.PATH + '/Map/Map{}.png')


if __name__ == '__main__':
  intents = discord.Intents.default()
  intents.message_content = True
  client = MyClient(intents=intents)
  tree= app_commands.CommandTree(client)
  updt()
  

  @tree.command(name='event_filter', description='Filtra gli eventi per regione', guild=discord.Object(id=client.server))
  async def filter(interaction: discord.Interaction):
    if interaction.user.id in defs.DB['permission']:
      view = discord.ui.View()
      eventFilter = classes.EventFilter(await get_database(client), client)
      view.add_item(eventFilter)
      await interaction.response.send_message('Seleziona le regioni di interesse:', view=view, ephemeral=True)
      #await eventFilter.wait()


  @tree.command(name='depot_add', description='Aggiungi i dati di un deposito', guild=discord.Object(id=client.server))
  @discord.app_commands.describe(
    location='Inserisci la posizione del deposito',
  )
  @discord.app_commands.autocomplete(location=location_autocomplete)
  async def deposito(interaction: discord.Interaction, location: str):
    modal = classes.DepotModal()
    await interaction.response.send_modal(modal)
    await modal.wait()
    data = await get_database(client)
    location = json.loads(location)
    data['depots'].append({
      'group': 'Altro' if modal.group.value=='' else modal.group.value, 
      'iconType': location[3], 
      'location': location[0], 
      'map': location[1],
      'x': location[4][0],
      'y': location[4][1],
      'name': modal.name.value, 
      'passcode': modal.passcode.value, 
      'desc': modal.desc.value
    })
    depots = data['depots']
    
    embed, view = classes.view_depots(depots[0]['group'], depots)

    await client.depotChannel.send(file=embed.fileMap, embed=embed, view=view)
    await modal.interaction.delete_original_response()
    await interaction.followup.send(f'Deposito a {location[0]} aggiunto', ephemeral=True)
    #await client.depotChannel.send(embed=embed)

    async for msg in client.depotChannel.history(limit=100):
      if msg.id == data['depotListMsg']:
        await msg.delete()
    data['depotListMsg'] = client.depotChannel.last_message_id

    await updt_database(data, client)


  @tree.command(name='depot_remove', description='Elimina un deposito', guild=discord.Object(id=client.server))
  @discord.app_commands.describe(
    depot='Seleziona un deposito da eliminare'
  )
  @discord.app_commands.autocomplete(depot=get_depot)
  async def deposito(interaction: discord.Interaction, depot: int):
    data = await get_database(client)
    loc = data['depots'][depot]['location']
    data['depots'].remove(data['depots'][depot])
    depots = data['depots']

    await interaction.response.defer(thinking=True, ephemeral=True)

    embed, view = classes.view_depots(depots[0]['group'], depots)

    await client.depotChannel.send(file=embed.fileMap, embed=embed, view=view)
    await interaction.followup.send(f"Deposito a {loc} rimosso", ephemeral=True)
    #await client.depotChannel.send(embed=embed)

    async for msg in client.depotChannel.history(limit=100):
      if msg.id == data['depotListMsg']:
        await msg.delete()
    data['depotListMsg'] = client.depotChannel.last_message_id

    await updt_database(data, client)


  @tree.command(name='reset', description='Fai un reset del bot', guild=discord.Object(id=client.server))
  async def reset(interaction: discord.Interaction):
    data = await get_database(client)

    data['download'] = 0
    await updt_database(data, client)
    await client.change_presence(status=discord.Status.idle)
    await interaction.response.defer(ephemeral=True, thinking=True)
    #updateMapL()
    mapName = defs.MAP_NAME

    first = True
    for map in mapName:
      newData = downloadData(map, 2)
      updateData(map, newData, 2)
      setName(map)
      if first:
        str_1 = loading(mapName.index(map)+1, len(mapName))
        await interaction.followup.send(f'Data {map} updated\n' + str_1)
        first = False
      else:
        str_1 = loading(mapName.index(map)+1, len(mapName))
        await interaction.edit_original_response(content=f'Data {map} updated\n' + str_1)
    print("Data updated")
    str_1 = 'Data updated\n' + str_1 + '\n\n'
    await interaction.edit_original_response(content=str_1)

    for map in mapName:
      data = read(defs.DB['mapData'].format(map))
      updateMap(map, data)
      str_2 = loading(mapName.index(map)+1, len(mapName))
      await interaction.edit_original_response(content= str_1 + f'Map {map} updated\n' + str_2)
    print("Maps updated")
    str_2 = 'Maps updated\n' + str_2 + '\n\n'
    await interaction.edit_original_response(content=str_1 + str_2 +'Reset e update dati effettuati')
    await interaction.edit_original_response(content='Reset e update dati effettuati')
    await client.change_presence(status=discord.Status.online)

    #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']
  
  '''
  @tree.error
  async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    await client.errorChannel.send(error)
  '''

  client.run(defs.DB['Token'])
