from multiprocessing import Event
import traceback
import discord
from discord import app_commands
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
      try:
        mapName = get_topic(self.get_channel(defs.DB['eventThread']))
        for map in defs.MAP_NAME:
          list = []
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
                flag = convert_to_bin(newData['mapItems'][j]['flags'])
                if newData['mapItems'][j]['teamId'] != oldData['mapItems'][i]['teamId'] and flag[3] != '1' and (map in mapName or flag[1] == '1'):
                  list.append(j)

            if len(list) > 0:
              newData = newData['mapItems']
              oldData = oldData['mapItems']
              data = downloadData(map, 0)
              data['mapItems'] = newData
              updateData(map, newData, 1)
              updateMap(map, data, -1)
              faction = search_faction(newData)

            for i in list:
              if i >= 0 and newData[i]['iconType'] in defs.DB['iconFilter']:
                channel = self.get_channel(defs.DB['eventThread'])

                addCircle(map, (newData[i]['x'], newData[i]['y']))
                icon = defs.ICON_ID[newData[i]['iconType']]
                
                j = search_item(newData[i], oldData)
                flag = convert_to_bin(newData[i]['flags'])
                message, color = switch(map, newData[i]['teamId'], oldData[j]['teamId'], i, flag)

                if color:
                  color = 0x65875E
                else:
                  color = 0x2D6CA1
                
                description = icon + message
                embed=discord.Embed(title=description, color=color)
                
                if newData[i]['teamId'] == 'COLONIALS':
                  color = 1
                  if flag[1] == '1':
                    color = 2
                  changeColor(Image.open(defs.DB['iconImage'].format(icon)), color).save(defs.PATH + '/data/tempIcon.png')
                  fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
                  embed.set_image(url='attachment://tempIcon.png'.format(icon))
                elif newData[i]['teamId'] == 'WARDENS':
                  color = 0
                  if flag[1] == '1':
                    color = 2
                  changeColor(Image.open(defs.DB['iconImage'].format(icon)), color).save(defs.PATH + '/data/tempIcon.png')
                  fileIcon = discord.File(defs.PATH + '/data/tempIcon.png')
                  embed.set_image(url='attachment://tempIcon.png'.format(icon))
                else:
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

                await channel.send(files = files, embed=embed)


          await asyncio.sleep(1)

      except:
        print(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n')
        self.get_channel(defs.DB['errorChannel']).send(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n')

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
  print("Maps updated")

  #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']


def switch(map, newTeam, oldTeam, index, flag):
  message = ''
  data = read(defs.DB['mapData'].format(map))
  nuke = False
  for item in data['mapTextItems']:
    if item['mapMarkerType'] == 'Major' and item['location'] == index:
      message = item['text']
      if item['text'] == 'RocketSite':
        nuke = True
  
  message = ' di ' + message + '{}'
  msg = [message, message]
  if flag[5] == '1':
    msg[0] = message + '\nLa regione {} è stata persa!'.format(map)
    msg[1] = message + '\nLa regione {} è stata conquistata!'.format(map)



  try:
    #icona vicina a dove
    if flag[1] != '1':
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
    else:
      if nuke:
        if newTeam == 'COLONIALS':
          return msg[1].format(' è stata lanciata!'), 1
        else:
          return msg[0].format(' è stata lanciata!'), 0
      else:
        if oldTeam == 'COLONIALS':
          return msg[0].format(' ha fatto boom'), 0
        else:
          return msg[1].format(' ha fatto boom'), 1
  except:
    print(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')
    client.get_channel(defs.DB['errorChannel']).send(time.asctime(time.localtime(time.time())) + '\n' + traceback.format_exc() + '\n', msg, '\n')


def get_topic(channel):
  str = channel.topic
  str = str.split('\n')[1]
  list = str.split(', ')
  maps = []
  for map in defs.MAP_NAME:
    if map in list:
      maps.append(map)
  return maps


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


#@tree.command(name='help', description='test', guild=discord.Object(id=client.server))

if __name__ == '__main__':
  client = MyClient(intents=discord.Intents.default())
  tree= app_commands.CommandTree(client)
  updt()
  client.run(defs.DB['Token'])


  @tree.command(name='presenze', description='Crea un annuncio per reclutare', guild=discord.Object(id=client.server))
  @discord.app_commands.describe(mode='Vuoi creare un nuovo annuncio o stampare la lista delle presenze?')
  @discord.app_commands.choices(mode=[
    discord.app_commands.Choice(name='new', value=0),
    discord.app_commands.Choice(name='list_users', value=1)
  ])
  async def presenze(interaction: discord.Interaction, mode: discord.app_commands.Choice[int]):
    if interaction.user.id in defs.DB['permission']:
      if mode.value:
        list = classes.get_presenze()
        str = '\n'.join(list)
        await interaction.response.send_message(str, ephemeral=True)
      else:
        await interaction.response.send_modal(classes.Presenze(  ))
    else:
      await interaction.response.send_message('Non hai i permessi', ephemeral=True)


  @tree.command(name='annuncio', description='Crea un annuncio personalizzato', guild=discord.Object(id=client.server))
  @discord.app_commands.describe(
    image="Vuoi inserire un'immagine? (Non ancora disponibile)"
  )
  @discord.app_commands.choices(image=[
    discord.app_commands.Choice(name='yes', value=1),
    discord.app_commands.Choice(name='no', value=0)
  ])
  async def annuncio(interaction: discord.Interaction, image: discord.app_commands.Choice[int]):
    if interaction.user.id in defs.DB['permission']:
      await interaction.response.send_modal(classes.Annuncio(image))
    else:
      await interaction.response.send_message('Non hai i permessi', ephemeral=True)


  @tree.command(name='event_filter', description='Filtra gli eventi per regione', guild=discord.Object(id=client.server))
  async def filter(interaction: discord.Interaction):
    if interaction.user.id in defs.DB['permission']:
      view = discord.ui.View()
      view.add_item(classes.EventFilter(client.get_channel(defs.DB['eventThread'])))
      await interaction.response.send_message('Seleziona le regioni di interesse:', view=view, ephemeral=True)


  @tree.command(name='reset', description='Fai un reset del bot', guild=discord.Object(id=client.server))
  async def reset(interaction: discord.Interaction):
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
      updateMap(map, data, -1)
      str_2 = loading(mapName.index(map)+1, len(mapName))
      await interaction.edit_original_response(content= str_1 + f'Map {map} updated\n' + str_2)
    print("Maps updated")
    str_2 = 'Maps updated\n' + str_2 + '\n\n'
    await interaction.edit_original_response(content=str_1 + str_2 +'Reset e update dati effettuati')
    await interaction.edit_original_response(content='Reset e update dati effettuati')
    await client.change_presence(status=discord.Status.online)

    #DB['startWar'] = requests.get(DB['warReport']).json()['conquestStartTime']

