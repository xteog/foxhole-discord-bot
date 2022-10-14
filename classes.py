from multiprocessing.sharedctypes import Value
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
            data = read(defs.DB['mapData'].format(map))['mapTextItems']
            for name in data:
                if name['mapMarkerType'] == 'Major':
                    options.append(discord.SelectOption(label=name['text'], description='Colonials'))
            super().__init__(placeholder=f'Provincia di {map}', min_values=1, max_values=1, options=options)
        else:
            options = [discord.SelectOption(label='Nessuna')]
            super().__init__(placeholder='   ', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] != 'Nessuna':
            self.em.description += f'\n\n``{self.values[0]} ({self.map})``'
        else:
            self.em.add_field(name = self.map, value=8)
        await interaction.response.send_message(embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions(everyone=True))


class SelectRegion(discord.ui.Select):
    def __init__(self, em, emojis, default):
        self.em = em
        self.emojis = emojis
        options = [discord.SelectOption(label='Nessuna')]
        for map in defs.MAP_NAME[0:24]:
            desc = ''
            data = read(defs.DB['mapData'].format(map))
            for i in data['mapItems']:
                if i['flags'] == 41:
                    if i['teamId'] == 'COLONIALS':
                        desc = 'Colonials'
                        icon = emojis[0]
                    elif i['teamId'] == 'WARDENS':
                        desc = 'Wardens'
                        icon = emojis[1]
            if default == map:
                options.append(discord.SelectOption(label=map, description=desc, emoji=icon, default=True))
            else:
                options.append(discord.SelectOption(label=map, description=desc, emoji=icon))
        super().__init__(placeholder='Regione', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] != 'Nessuna':
            await interaction.response.edit_message(view=SelectViewRegion(self.em, self.emojis, self.values[0]))
        else:
            await interaction.response.send_message(embed=self.em, view=JoinButton(self.em), allowed_mentions=discord.AllowedMentions(everyone=True))


class SelectViewRegion(discord.ui.View):
    def __init__(self, em, emojis, map):
        super().__init__()
        self.add_item(SelectRegion(em, emojis, map))
        self.add_item(SelectZone(em, map))


class Presenze(discord.ui.Modal, title='Presenze'):
    def __init__(self, emojis):
        super().__init__()
        global presenze
        presenze = []
        self.emojis = emojis
        self.titolo = discord.ui.TextInput(label="Titolo", placeholder="Inserisci il titolo dellannuncio")
        self.descrizione = discord.ui.TextInput(label="Descrizione", required=False, placeholder="Inserisci la descrizione dellannuncio",  style=discord.TextStyle.paragraph)
        self.add_item(self.titolo)
        self.add_item(self.descrizione)

    async def on_submit(self, interaction: discord.Interaction):
        em = discord.Embed(title=self.titolo.value, description='@everyone '+self.descrizione.value)
        em.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        em.set_footer(text='Joined: 0')
        await interaction.response.send_message('Seleziona la regione:', view=SelectViewRegion(em, self.emojis, ''), ephemeral=True)


def get_presenze():
    try:
        return presenze
    except:
        return ['Usa /presenze per fare un annuncio']
