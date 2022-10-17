import defs
import discord
from testRequest import read

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
            data = read(defs.DB['mapData'].format(map))
            for name in data['mapTextItems']:
                if name['mapMarkerType'] == 'Major':
                    item = data['mapItems'][name['location']]
                    icon = item['iconType']
                    if item['teamId'] == 'COLONIALS':
                        str = f'{icon}C' 
                    elif item['teamId'] == 'WARDENS':
                        str = f'{icon}W' 
                    else:
                        str = f'{icon}'
                    emoji = discord.PartialEmoji(name=defs.DB['emojis'][str][0], id=defs.DB['emojis'][str][1])
                    options.append(discord.SelectOption(label=name['text'], description='Colonials', emoji=emoji))
            super().__init__(placeholder=f'Provincia di {map}', min_values=1, max_values=1, options=options)
        else:
            options = [discord.SelectOption(label='Nessuna')]
            super().__init__(placeholder='   ', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] != 'Nessuna':
            self.em.description += f'\n\n``{self.values[0]} ({self.map})``'
        else:
            self.em.add_field(name = self.map, value=8)

        view = make_view(self.map, self.values[0])
        await interaction.response.edit_message(view=view)
        await interaction.followup.send('@everyone', embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions(everyone=True))


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
            await interaction.response.send_message(embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions(everyone=True))


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
    def __init__(self, fields, image):
        super().__init__()
        self.fieldsTitolo = []
        self.fieldsDescrizione = []
        self.titolo = discord.ui.TextInput(label="Titolo", placeholder="Inserisci il titolo dell'annuncio")
        self.descrizione = discord.ui.TextInput(label="Descrizione", required=False, placeholder="Inserisci la descrizione dell'annuncio",  style=discord.TextStyle.paragraph)
        self.add_item(self.titolo)
        self.add_item(self.descrizione)
        for i in range(fields):
            self.fieldsTitolo.append(discord.ui.TextInput(label=f"Titolo field {i+1}", placeholder=f"Inserisci il titolo del field"))
            self.fieldsDescrizione.append(discord.ui.TextInput(label=f"Descrizione field {i+1}", required=False, placeholder="Inserisci la descrizione del field",  style=discord.TextStyle.paragraph))
            self.add_item(self.fieldsTitolo[-1])
            self.add_item(self.fieldsDescrizione[-1])

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.titolo.value, description='@everyone '+self.descrizione.value, color=0xFAA81A)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        for i in range(len(self.fieldsTitolo)):
            embed.add_field(name=self.fieldsTitolo[i], value=self.fieldsDescrizione[i])
        #file = discord.File(DB['mapImage'].format(map))
        #embed.set_image(url='attachment://{}.png'.format)
        await interaction.response.send_message(embed=embed)


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
