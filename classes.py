from testImage import highlight_name
import defs
import discord
from testRequest import read, write

class JoinButton(discord.ui.View):
    def __init__(self, em):
        self.em = em
        super().__init__(timeout=86400)

    @discord.ui.button(label='Ci sono!', style=discord.ButtonStyle.primary)
    async def my_button(self, interaction: discord.Interaction, button: discord.ui.Button,):
        if interaction.user.name in presenze:
            await interaction.response.send_message('Ti sei già unito', ephemeral=True)
        else:
            presenze.append(interaction.user.name)
            print(presenze)
            joined = int(self.em.footer.text.split(' ')[1]) + 1
            self.em.set_footer(text=f'Joined: {joined}')
            await interaction.response.edit_message(embed=self.em)


class SelectZone(discord.ui.Select):
    def __init__(self, em, map):
        self.em = em
        self.map = map
        if map != '':
            options = [discord.SelectOption(label='Nessuna')]
            self.data = read(defs.DB['mapData'].format(map))
            for name in self.data['mapTextItems']:
                if name['mapMarkerType'] == 'Major':
                    item = self.data['mapItems'][name['location']]
                    icon = item['iconType']
                    if item['teamId'] == 'COLONIALS':
                        str = f'{icon}C' 
                    elif item['teamId'] == 'WARDENS':
                        str = f'{icon}W' 
                    else:
                        str = f'{icon}'
                    emoji = discord.PartialEmoji(name=defs.DB['emojis'][str][0], id=defs.DB['emojis'][str][1])
                    options.append(discord.SelectOption(label=name['text'], value=self.data['mapTextItems'].index(name),description='Colonials', emoji=emoji))
            super().__init__(placeholder=f'Provincia di {map}', min_values=1, max_values=1, options=options)
        else:
            options = [discord.SelectOption(label='Nessuna')]
            super().__init__(placeholder='   ', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] != 'Nessuna':
            self.em.description += f"\n\n``{self.data['mapTextItems'][int(self.values[0])]['text']} ({self.map})``"
            highlight_name(self.map, int(self.values[0]))
            fileMap = discord.File(defs.PATH + '/data/tempImage.png')
            self.em.set_thumbnail(url='attachment://tempImage.png')
            view = make_view(self.map, self.data['mapTextItems'][int(self.values[0])]['text'])
        else:
            self.em.description += f"\n\n``{self.map}``"
            view = make_view(self.map, self.values[0])

        await interaction.response.edit_message(view=view)
        await interaction.followup.send(file=fileMap, content='@Miles', embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions.all())


class SelectRegion(discord.ui.Select):
    def __init__(self, em, default):
        self.em = em
        options = [discord.SelectOption(label='Nessuna')]
        for map in defs.MAP_NAME[0:24]:
            desc = ''
            data = read(defs.DB['mapData'].format(map))
            for i in data['mapItems']:
                if i['flags'] == 41:
                    if i['teamId'] == 'COLONIALS':
                        desc = 'Colonials'
                        icon = discord.PartialEmoji(name=defs.DB['emojis']['ColonialLogo'][0], id=defs.DB['emojis']['ColonialLogo'][1])
                    elif i['teamId'] == 'WARDENS':
                        desc = 'Wardens'
                        icon = discord.PartialEmoji(name=defs.DB['emojis']['WardenLogo'][0], id=defs.DB['emojis']['WardenLogo'][1])
                    else:
                        icon = None
            if default == map:
                options.append(discord.SelectOption(label=map, description=desc, emoji=icon, default=True))
            else:
                options.append(discord.SelectOption(label=map, description=desc, emoji=icon))
        super().__init__(placeholder='Regione', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] != 'Nessuna':
            await interaction.response.edit_message(view=SelectViewRegion(self.em, self.values[0]))
        else:
            view = make_view('Nessuna', 'Nessuna')
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions.all())


class SelectViewRegion(discord.ui.View):
    def __init__(self, em, map):
        super().__init__()
        self.add_item(SelectRegion(em, map))
        self.add_item(SelectZone(em, map))


class Presenze(discord.ui.Modal, title='Presenze'):
    def __init__(self):
        super().__init__()
        global presenze
        presenze = []
        self.titolo = discord.ui.TextInput(label="Titolo", placeholder="Inserisci il titolo dellannuncio")
        self.descrizione = discord.ui.TextInput(label="Descrizione", required=False, placeholder="Inserisci la descrizione dellannuncio",  style=discord.TextStyle.paragraph)
        self.add_item(self.titolo)
        self.add_item(self.descrizione)

    async def on_submit(self, interaction: discord.Interaction):
        em = discord.Embed(title=self.titolo.value, description=self.descrizione.value, color=0xFAA81A)
        em.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        em.set_footer(text='Joined: 0')
        await interaction.response.send_message('Seleziona la regione:', view=SelectViewRegion(em, ''), ephemeral=True)


class Annuncio(discord.ui.Modal, title='Annuncio'):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.fieldsTitolo = []
        self.fieldsDescrizione = []
        self.titolo = discord.ui.TextInput(label="Titolo", placeholder="Inserisci il titolo dell'annuncio")
        self.descrizione = discord.ui.TextInput(label="Descrizione", required=False, placeholder="Inserisci la descrizione dell'annuncio",  style=discord.TextStyle.paragraph)
        self.add_item(self.titolo)
        self.add_item(self.descrizione)


    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.titolo.value, description=self.descrizione.value, color=0xFAA81A)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        for i in range(len(self.fieldsTitolo)):
            embed.add_field(name=self.fieldsTitolo[i], value=self.fieldsDescrizione[i])
        
        if self.image:
            print('Non ancora disponibile')
            '''
            view = discord.ui.View()
            view.add_item(discord.ui.TextInput(label='ciao'))
            await interaction.response.send_message('Seleziona la regione:',view=view)
        '''
        #file = discord.File(DB['mapImage'].format(map))
        #embed.set_image(url='attachment://{}.png'.format)
        await interaction.response.send_message(embed=embed)


class EventFilter(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label='Tutte')]
        for map in defs.MAP_NAME[0:24]:
            desc = ''
            data = read(defs.DB['mapData'].format(map))
            for i in data['mapItems']:
                if i['flags'] == 41:
                    if i['teamId'] == 'COLONIALS':
                        desc = 'Colonials'
                        icon = discord.PartialEmoji(name=defs.DB['emojis']['ColonialLogo'][0], id=defs.DB['emojis']['ColonialLogo'][1])
                    elif i['teamId'] == 'WARDENS':
                        desc = 'Wardens'
                        icon = discord.PartialEmoji(name=defs.DB['emojis']['WardenLogo'][0], id=defs.DB['emojis']['WardenLogo'][1])
                    else:
                        icon = None
            options.append(discord.SelectOption(label=map, description=desc, emoji=icon))
        super().__init__(placeholder='Regione', min_values=1, max_values=25, options=options)

    async def callback(self, interaction: discord.Interaction):
        with open(defs.DB['mapName'], 'w') as f:
            if 'Tutte' in self.values:
                write(defs.DB['mapName'], defs.MAP_NAME)
                await interaction.response.send_message('Regioni di interesse:\nTutte')
            else:
                write(defs.DB['mapName'], self.values)
                str = 'Regioni di interesse:\n' + self.values[0]
                for i in range(1, len(self.values)):
                    str += ', ' + self.values[i]
                await interaction.response.send_message(str)


def make_view(map, region):
    data = read(defs.DB['mapData'].format(map))
    for i in data['mapItems']:
        if i['flags'] == 41:
            if i['teamId'] == 'COLONIALS':
                desc = 'Colonials'
                icon = discord.PartialEmoji(name=defs.DB['emojis']['ColonialLogo'][0], id=defs.DB['emojis']['ColonialLogo'][1])
            elif i['teamId'] == 'WARDENS':
                desc = 'Wardens'
                icon = discord.PartialEmoji(name=defs.DB['emojis']['WardenLogo'][0], id=defs.DB['emojis']['WardenLogo'][1])
    view = discord.ui.View()
    view.add_item(discord.ui.Select(options=[discord.SelectOption(label=map, emoji=icon, default=True)], disabled=True))
    for name in data['mapTextItems']:
        if name['text'] == region:
            item = data['mapItems'][name['location']]
            icon = item['iconType']
            if item['teamId'] == 'COLONIALS':
                str = f'{icon}C' 
            elif item['teamId'] == 'WARDENS':
                str = f'{icon}W' 
            else:
                str = f'{icon}'
            icon = discord.PartialEmoji(name=defs.DB['emojis'][str][0], id=defs.DB['emojis'][str][1])
    view.add_item(discord.ui.Select(options=[discord.SelectOption(label=region, emoji=icon, default=True)], disabled=True))
    return view


def get_presenze():
    try:
        return presenze
    except:
        return ['Usa ``/presenze`` per fare un annuncio']
