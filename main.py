from secrets import choice
import discord
from discord import app_commands
from discord.ext import tasks
from testRequest import updateData, downloadData, updateMapL, read, setName
from testImage import updateMap, addCircle, changeColor
import time
import defs
from PIL import Image
import classes
import asyncio


class MyClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.server = defs.DB['serverId']


  async def setup_hook(self) -> None:
    self.bg_task = self.loop.create_task(self.background_task())


  async def on_ready(self):
    await tree.sync(guild = discord.Object(id=self.server))
    print('We have logged in as {}'.format(self.user.name))
    await client.change_presence(status=discord.Status.online)


  async def background_task(self):
    await self.wait_until_ready()
    while not self.is_closed():
      await asyncio.sleep(10)
      mapName = defs.MAP_NAME
      for map in mapName:
        list = []
        print(map)
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
              elif newData['mapItems'][j]['teamId'] != oldData['mapItems'][i]['teamId'] and newData['mapItems'][j]['flags'] != 4:
                list.append(j)

          if len(list) > 0:
            newData = newData['mapItems']
            oldData = oldData['mapItems']
            data = downloadData(map, 0)
            data['mapItems'] = newData
            updateData(map, newData, 1)
            updateMap(map, data, -1)

          for i in list:
            if newData[i]['iconType'] in defs.DB['iconFilter']:
              channel = self.get_channel(defs.DB['eventThread'])

              addCircle(map, (newData[i]['x'], newData[i]['y']))
              icon = defs.ICON_ID[newData[i]['iconType']]
              j = search_item(newData[i], oldData)
              message, color = switch(map, newData[i]['teamId'], oldData[j]['teamId'], i, newData[i]['flags'])

              if color:
                color = 0x65875E
              else:
                color = 0x2D6CA1

              description = icon + message
              if newData[i]['teamId'] == 'COLONIALS':
                changeColor(Image.open(defs.DB['iconImage'].format(icon)), True).save(defs.PATH + '/data/tempIcon.png')
                fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
              elif newData[i]['teamId'] == 'WARDENS':
                changeColor(Image.open(defs.DB['iconImage'].format(icon)), False).save(defs.PATH + '/data/tempIcon.png')
                fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
              else:
                fileIcon = discord.File(defs.DB['iconImage'].format(icon))
              fileMap = discord.File(defs.PATH + '/data/tempImage.png')
              embed=discord.Embed(title=description, color=color)
              embed.set_author(name=map, icon_url='attachment://{}.png'.format(icon))
              embed.set_thumbnail(url='attachment://tempImage.png')
              d, h, m = timeWar(data['lastUpdated'])
              embed.set_footer(text = f'{d}d {h}h {m}m')

              await channel.send(files = [fileMap, fileIcon], embed=embed)

        await asyncio.sleep(1)

    '''
    except:
      with open('./data/errors.txt', 'a') as file:
        file.write(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n')
    '''


  async def on_message(self, message):
    global presenze
    if message.author == client.user:
      presenze = message

    msg = message.content

    if msg.startswith('$map'):
      for map in self.mapName:
        data = read(defs.DB['mapData'].format(map))
        updateMap(map, data, -1)
        print(map + "finished")

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


client = MyClient(intents=discord.Intents.default())
tree= app_commands.CommandTree(client)

@tree.command(name='presenze', description='test', guild=discord.Object(id=client.server))
@discord.app_commands.describe(mode='prova')
@discord.app_commands.choices(mode=[
  discord.app_commands.Choice(name='init', value=0),
  discord.app_commands.Choice(name='list_users', value=1)
])
async def presenze(interaction: discord.Interaction, mode: discord.app_commands.Choice[int]):
  if mode.value:
    list = classes.get_presenze()
    str = '\n'.join(list)
    await interaction.response.send_message(str)
  else:
    await interaction.response.send_modal(classes.Presenze(client.emojis))


@tree.command(name='reset', description='test', guild=discord.Object(id=client.server))
async def reset(interaction: discord.Interaction):
  await client.change_presence(status=discord.Status.idle)
  await interaction.response.defer(ephemeral=True, thinking=False)
  updateMapL()
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
    updateMap(map, data, -1)
    str_2 = loading(mapName.index(map)+1, len(mapName))
    await interaction.edit_original_response(content= str_1 + f'Map {map} updated\n' + str_2)
  print("Maps updated")
  str_2 = 'Maps updated\n' + str_2 + '\n\n'
  await interaction.edit_original_response(content=str_1 + str_2 +'Reset e update dati effettuati')
  await interaction.edit_original_response('Reset e update dati effettuati')
  await client.change_presence(status=discord.Status.online)

  #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']


client.run(defs.DB['Token'])
