import discord
from discord.ext import commands
import datetime
import discord.ui
from discord.ui import View, Button, Select
import requests
import aiohttp


TOKEN = "x"  # Tu token de autenticación
DISCORD_BOT_TOKEN = "x"  # Tu token de bot de Discord
HEADERS = {"Authorization": f"Token {TOKEN}"}
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')

async def get_bot_configuration(server_id):
    url = f"https://www.pyticket.xyz/api/bot_configuration/{server_id}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print("Error")
                return None
            else:
                print("Success")
                return await response.json()

@bot.event
async def on_ready():
    print(f'BOT IS READY {bot.user}!')

async def close_ticket(interaction: discord.Interaction):
    await interaction.message.channel.delete()

@bot.event
async def on_interaction(interaction):
    if interaction.data["custom_id"] == "closeticket":
        if interaction.channel.category.name == "Tickets" and interaction.channel.name.endswith("-ticket"):
            await interaction.channel.delete()
            await interaction.response.send_message("Ticket cerrado con éxito!", ephemeral=True)
        else:
            await interaction.response.send_message("No se puede cerrar este canal como un ticket!", ephemeral=True)

async def ticketcallback(interaction: discord.Interaction):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Pyticket")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True),
        role: discord.PermissionOverwrite(view_channel=True)
    }
    
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")

    channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
    
    bot_config = await get_bot_configuration(str(guild.id))
    if bot_config is None:
        ticket_title = "Titulo ticket ya creado"
        ticket_description = "Descripcion ticket ya creado"
        creation_message = "Mensaje de creacion en - "
        welcome_message = f"{interaction.user.mention} Mensaje bienvenida al ticket!"
    else:
        ticket_title = bot_config.get('ticket_title', "Titulo ticket ya creado")
        ticket_description = bot_config.get('ticket_description', "Descripcion ticket ya creado")
        creation_message = bot_config.get('creation_message', "Mensaje de creacion en - ")
        welcome_message = bot_config.get('welcome_message', f"{interaction.user.mention} Mensaje bienvenida al ticket!")

    embed = discord.Embed(title=ticket_title, description=ticket_description, color=0x2F0FF)
    embed.set_author(name=f"{creation_message} {channel}", icon_url="https://i.pinimg.com/474x/87/68/24/876824329175692f223dbe72b675d0b0.jpg")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label='Close', custom_id='closeticket'))
    await interaction.response.send_message(f"Mensaje de creacion en - <#{channel.id}>", ephemeral=True)

    await channel.send(welcome_message)
    await channel.send(embed=embed, view=view)


@bot.command()
async def ticket(ctx):
    """ create button with emoji """
    embed = discord.Embed()
    embed.add_field(name="Titulo ", value="Descripcion", inline=False)
    embed.set_footer(text="Created by: @Z3r0", icon_url="https://i.pinimg.com/474x/87/68/24/876824329175692f223dbe72b675d0b0.jpg")
    button = discord.ui.Button(label="Create Ticket 📩", style=discord.ButtonStyle.blurple)
    button.callback = ticketcallback
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    await ctx.send("MENSAJE CREACIÓN 📩", view=view, embed=embed)


@bot.event
async def on_guild_join(guild):
    url = "https://www.pyticket.xyz/add_server/"
    data = {
        'server_id': str(guild.id),
        'owner_id': str(guild.owner_id),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                print(f"Error al añadir el servidor {guild.id} a la base de datos.")
            else:
                print(f"Servidor {guild.id} añadido a la base de datos.")

@bot.event
async def on_guild_update(before, after):
    if before.member_count != after.member_count:
        server_id = str(after.id)
        member_count = after.member_count

        url = f"https://www.pyticket.xyz/api/update_server_info/"
        data = {
            'server_id': server_id,
            'member_count': member_count,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=HEADERS, data=data) as response:
                if response.status != 200:
                    print(f"Error al actualizar la información del servidor {server_id}.")
                else:
                    print(f"Información del servidor {server_id} actualizada.")

bot.run(DISCORD_BOT_TOKEN)