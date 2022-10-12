import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from testRequest import updateData, downloadData, updateMapL, read, setName
from testImage import updateMap, addCircle, changeColor
import time
import defs
from PIL import Image

presenze = 0

class MyClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.channel = defs.DB['channelId']
    self.presence = 0
    self.reac_users = []

  async def setup_hook(self) -> None:
    self.bg_task = self.loop.create_task(self.my_background_task())

  async def on_ready(self):
    print('We have logged in as {}'.format(self.user.name))
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('FoxHole'))


  async def my_background_task(self):
    while(True):
      await self.wait_until_ready()
      while not self.is_closed():
        startT = time.time()
        mapName = defs.MAP_NAME
        for map in mapName:
          list = []
          cond = 0
          data = downloadData(map, 1)
          newData = data
          oldData = read(defs.DB['mapData'].format(map))
          if oldData == 0: #aggiusta
            updateData(map, newData, 1)
          else:
            if newData['lastUpdated'] != oldData['lastUpdated']:
              l = len(oldData['mapItems'])
              for i in range(l):
                j = search_item(oldData['mapItems'][i], newData['mapItems'])
                if j == -1:
                  print(f"object destroyed: {oldData['mapItems'][i]['iconType']}, {map}") #print message INtel center
                elif newData['mapItems'][j]['teamId'] != oldData['mapItems'][i]['teamId'] and newData[j]['flags'] != 4:
                  list.append(j)

            if len(list) > 0:
              newData = newData['mapItems']
              oldData = oldData['mapItems']
              data = downloadData(map, 0)
              data['mapItems'] = newData
              updateData(map, newData, 1)
              updateMap(map, data, -1)

            for i in list:
              #icon = iconId[newData[i]['iconType']]
              channel = self.get_channel(self.channel)

              addCircle(map, (newData[i]['x'], newData[i]['y']))
              icon = defs.ICON_ID[newData[i]['iconType']]
              j = search_item(newData[i], oldData)
              message, color = switch(map, newData[i]['teamId'], oldData[j]['teamId'], i, newData[i]['flags'])

              if color:
                color = 0x65875E
              else:
                color = 0x2D6CA1

              description = icon + message
              fileIcon = discord.File(defs.DB['iconImage'].format(icon))
              if newData[i]['teamId'] == 'COLONIALS':
                fileIcon =changeColor(Image.open(defs.DB['iconImage'].format(icon)), True)
              elif newData[i]['teamId'] == 'WARDENS':
                fileIcon =changeColor(Image.open(defs.DB['iconImage'].format(icon)), False)
              fileMap = discord.File(defs.PATH + '/data/tempImage.png')
              fileIcon = discord.File(defs.DB['iconImage'].format(icon))
              if newData[i]['teamId'] == 'COLONIALS':
                icon =changeColor(Image.open(defs.DB['iconImage'].format(icon)), True)
              elif newData[i]['teamId'] == 'WARDENS':
                icon =changeColor(Image.open(defs.DB['iconImage'].format(icon)), False)
              embed=discord.Embed(title=description, color=color)
              embed.set_author(name=map, icon_url='attachment://{}.png'.format(icon))
              embed.set_thumbnail(url='attachment://tempImage.png')
              d, h, m = timeWar(data['lastUpdated'])
              embed.set_footer(text = f'{d}d {h}h {m}m')

              await channel.send(files = [fileMap, fileIcon], embed=embed)
                
              break
        
        #presenze
        if presenze != 1 and presenze != 0:
          channel = self.get_channel(channelId)
          for reaction in presenze.reactions:
            if len(await reaction.users().flatten()) != len(self.reac_users):
              async for user in reaction.users():
                self.reac_users.append(user.name)
              title = 'Presenze:'
              desc = ''
              for i in self.reac_users:
                desc = i + '\n' + desc
              embed=discord.Embed(title=title, description=desc, color=0xFF5733)
              embed.set_thumbnail(url=self.guilds.icon_url)
              await channel.send(embed=embed)

        with open(defs.PATH + '/data/time.txt', 'a') as file:  #Togli
          file.write(f'{int(time.time() - startT)}, ')

        await asyncio.sleep(60)
      '''
      except:
        with open('./data/errors.txt', 'a') as file:
          file.write(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n')
      '''


  async def on_message(self, message):
    global presenze
    if message.author == client.user and presenze == 1:
      presenze = message

    msg = message.content
    print(msg)
    if msg.startswith('$filter'):
      print(1)

    elif msg.startswith('$map'):
      for map in self.mapName:
        data = read(defs.DB['mapData'].format(map))
        updateMap(map, data, -1)
        print(map + "finished")

    elif msg.startswith('$updt'):
      updt()

    elif msg.startswith('$presenze'):
      channel = self.get_channel(channelId)
      msg = message
      await message.delete()
      presenze = 1
      #delete message
      title = 'Presenze'
      desc = ''
      com = msg.content.split('-')
      l = len(com)
      for i in range(l):
        if com[i].startswith('desc'):
          desc = com[i].split('"')[1]
      embed=discord.Embed(title=title, description=desc, color=0xFF5733)
      embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
      file = discord.File(defs.DB['serverIcon'])
      embed.set_thumbnail(url='attachment://serverIcon.png')
      #embed.set_image(url=.format)
      await channel.send(file=file, embed=embed)


    elif msg.startswith('$embed'):
      msg = message
      await message.delete()
      channel = self.get_channel(channelId)
      title = ''
      desc = ''
      com = msg.content.split('-')
      l = len(com)
      for i in range(l):
        if com[i].startswith('title'):
          title = com[i].split('"')[1]
        if com[i].startswith('desc'):
          desc = com[i].split('"')[1]
      embed=discord.Embed(title=title, description=desc, color=0xFF5733)
      embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
      #file = discord.File(DB['mapImage'].format(map))
      #embed.set_thumbnail(url=message.client.icon_url)
      #embed.set_image(url='attachment://{}.png'.format)
      await channel.send(embed=embed)


def updt():
  updateMapL()
  mapName = read(defs.DB['mapName'])

  for map in mapName:
    newData = downloadData(map, 2)
    updateData(map, newData, 2)
    setName(map)
  print("Data updated")

  for map in mapName:
    data = read(defs.DB['mapData'].format(map))
    updateMap(map, data, -1)
  print("Maps updated")

  #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']


def switch(map, newTeam, oldTeam, index, flag):
  message = '{}'
  if flag == 8 or flag == 41:
    data = read(defs.DB['mapData'].format(map))

    for item in data['mapTextItems']:
      if item['mapMarkerType'] == 'Major' and item['location'] == index:
        message = item['text']
    
    message = ' di ' + message + '{}'
  msg = [message, message]
  if flag == 41:
    msg[0] = message + '\nLa regione {} è stata persa!'.format(map)
    msg[1] = message + '\nLa regione {} è stata conquistata!'.format(map)

  #icona vicina a dove
  print(f'flag: {flag}')
  if newTeam == 'NONE':
    if oldTeam == 'COLONIALS':
      return msg[0].format(' è stato distrutto dai Wardens'), 0
    else:
      return msg[1].format(' è stato distrutto dai Colonials'), 1
  else:
    if newTeam == 'COLONIALS':
      return msg[1].format(' è stato conquistato dai Colonials'), 1
    else:
      return msg[0].format(' è stato conquistato dai Wardens'), 0

def timeWar(end):
  start = defs.DB['startWar']
  d = (end - start) / 86400000
  h = (d - int(d)) * 24
  m = (h - int(h)) * 60
  return int(d), int(h), int(m)


def search_item(item, data):
  l = len(data)
  found = -1
  for i in range(l):
    if item['x'] == data[i]['x'] and item['y'] == data[i]['y']:
      found = i
  return found

client = MyClient(intents=discord.Intents.default())

#updt()
client.run(defs.DB['Token'])
