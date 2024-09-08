import discord
from discord.ext import commands
from datetime import timedelta
import logging

logging.getLogger('discord').setLevel(logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

embed_color = 0x6c02ff

def has_role_or_permission(interaction: discord.Interaction, role_name: str, permission: str):
    """Verifica si el usuario tiene un rol específico o permiso."""
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role in interaction.user.roles:
        return True
    return getattr(interaction.user.guild_permissions, permission, False)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Se conecto al bot: {bot.user.name} correctamente!')

bot.activity = discord.Activity(type=discord.ActivityType.competing, name='Moonly')

@bot.tree.command(name="about", description="Información sobre el bot")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(title="Acerca de Moonly Assistant", color=embed_color)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Creador", value="<@1180995483997569028> (whoisaryyy)", inline=True)                                                   
    embed.add_field(name="Versión", value="1.0", inline=True)
    embed.add_field(name="Fecha de creación", value=f"<t:{int(bot.user.created_at.timestamp())}:D>", inline=False)
    embed.add_field(name="Descripción de Moonly Assistant", value="Este bot fue diseñado para apoyar a los moderadores de servidores de comunidades, ofreciendo herramientas funcionales y esenciales para mantener un entorno seguro y organizado. Desde la gestión de roles hasta la moderación de contenido, nuestro objetivo es simplificar tus tareas y mejorar la experiencia de tus miembros.", inline=False)
    embed.add_field(name="Nuestro servidor de soporte", value="https://discord.gg/moonlygg", inline=False)

    if bot.user.banner:
        embed.set_image(url=bot.user.banner.url)

    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name='userinfo', description='Muestra información del usuario')
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user

    embed = discord.Embed(title=f'Información de usuario - {user.name}', color=embed_color)

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(name='User', value=user.name, inline=False)
    embed.add_field(name='Display name', value=user.display_name, inline=False)
    embed.add_field(name='ID', value=user.id, inline=False)

    created_at = discord.utils.format_dt(user.created_at, style='R')
    embed.add_field(name='Se unió a Discord el', value=f'<t:{int(user.created_at.timestamp())}:D> ({created_at})', inline=False)

    joined_at = discord.utils.format_dt(user.joined_at, style='R')
    embed.add_field(name='Se unió al servidor el', value=f'<t:{int(user.joined_at.timestamp())}:D> ({joined_at})', inline=False)

    roles = [role.mention for role in user.roles if role.name != '@everyone']
    embed.add_field(name='Roles', value=', '.join(roles), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverinfo', description='Muestra información del servidor')
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f'Información del servidor {guild.name}', color=embed_color)
    embed.set_thumbnail(url=guild.icon.url)

    if guild.banner:
        embed.set_image(url=guild.banner.url)

    owner = guild.owner if guild.owner else await bot.fetch_user(guild.owner_id)

    online_members = len([member for member in guild.members if member.status != discord.Status.offline])

    embed.add_field(name='Nombre del servidor', value=guild.name, inline=True)
    embed.add_field(name='ID del servidor', value=guild.id, inline=True)
    embed.add_field(
        name='Dueño del servidor',
        value=f'{owner.mention} ``({owner.name})``' if owner else 'No disponible',
        inline=False
    )
    embed.add_field(name='Miembros totales', value=guild.member_count, inline=True)
    embed.add_field(name='Miembros en línea', value=online_members, inline=True)
    embed.add_field(name='Roles', value=len(guild.roles), inline=True)
    embed.add_field(name='Canales', value=len(guild.channels), inline=True)
    embed.add_field(name='Emojis', value=len(guild.emojis), inline=True)
    embed.add_field(name='Stickers', value=len(guild.stickers), inline=True)
    embed.add_field(
        name='Creación del servidor',
        value=f'<t:{int(guild.created_at.timestamp())}:D> ({discord.utils.format_dt(guild.created_at, style="R")})',
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='avatar', description='Muestra el avatar de un usuario')
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    avatar_url = user.avatar.url
    embed = discord.Embed(title=f'Avatar de {user.name}', color=embed_color)
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='banner', description='Muestra el banner de un usuario')
async def banner(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    
    user_profile = await bot.fetch_user(user.id)
    
    if user_profile.banner:
        banner_url = user_profile.banner.url
        embed = discord.Embed(title=f'Banner de {user.name}', color=embed_color)
        embed.set_image(url=banner_url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f'El usuario {user.name} no tiene un banner establecido.', ephemeral=True)

@bot.tree.command(name='ban', description='Banea a un usuario')
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    if not has_role_or_permission(interaction, 'RolModerador', 'ban_members'):
        await interaction.response.send_message("No tienes los permisos necesarios para banear usuarios.", ephemeral=True)
        return
    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f'El usuario {user.name} ha sido baneado')
    except discord.Forbidden:
        await interaction.response.send_message('No tengo permisos para banear a este usuario.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Ocurrió un error: {str(e)}', ephemeral=True)

@bot.tree.command(name='kick', description='Kickea a un usuario')
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    if not has_role_or_permission(interaction, 'RolModerador', 'kick_members'):
        await interaction.response.send_message("No tienes los permisos necesarios para kickear usuarios.", ephemeral=True)
        return
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f'El usuario {user.name} ha sido kickeado')
    except discord.Forbidden:
        await interaction.response.send_message('No tengo permisos para kickear a este usuario.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Ocurrió un error: {str(e)}', ephemeral=True)

@bot.tree.command(name='purge', description='Elimina una cantidad de mensajes en un canal')
async def purge(interaction: discord.Interaction, amount: int):
    if not has_role_or_permission(interaction, 'RolModerador', 'manage_messages'):
        await interaction.response.send_message("No tienes los permisos necesarios para eliminar mensajes.", ephemeral=True)
        return

    if amount < 1 or amount > 100:
        await interaction.response.send_message('La cantidad de mensajes debe ser entre 1 y 100', ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f'Se han eliminado {len(deleted)} mensajes')
    except discord.Forbidden:
        await interaction.followup.send('No tengo permisos para eliminar mensajes en este canal.', ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f'Ocurrió un error: {str(e)}', ephemeral=True)

@bot.tree.command(name='timeout', description='Aisla a un usuario')
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: str):
    if not has_role_or_permission(interaction, 'RolModerador', 'moderate_members'):
        await interaction.response.send_message("No tienes los permisos necesarios para aislar usuarios.", ephemeral=True)
        return

    if duration is None:
        await interaction.response.send_message('Debes proporcionar la duración del timeout (m, h, d)', ephemeral=True)
        return

    duration_parts = duration.split()
    duration_seconds = 0

    for part in duration_parts:
        if part.endswith('m'):
            duration_seconds += int(part[:-1]) * 60
        elif part.endswith('h'):
            duration_seconds += int(part[:-1]) * 3600
        elif part.endswith('d'):
            duration_seconds += int(part[:-1]) * 86400

    if duration_seconds <= 0:
        await interaction.response.send_message('La duración del timeout debe ser mayor a 0 segundos', ephemeral=True)
        return

    timeout_until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)

    try:
        await user.timeout(timeout_until)
        await interaction.response.send_message(f'El usuario {user.name} ha sido aislado por {duration}', ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message('No tengo permisos para aplicar un timeout a este usuario.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Ocurrió un error: {str(e)}', ephemeral=True)

@bot.tree.command(name='invite', description='Genera un enlace de invitación para el bot con los permisos necesarios')
async def invite(interaction: discord.Interaction):
    permissions = discord.Permissions(administrator=True)

    invite_url = discord.utils.oauth_url(bot.user.id, permissions=permissions)
    embed = discord.Embed(title='Invita al Bot', description=f'Invita al bot a tu servidor usando [este enlace]({invite_url}).', color=embed_color)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='ping', description='Muestra el ping del bot')
async def ping(interaction: discord.Interaction):
    ping = bot.latency * 1000
    await interaction.response.send_message(f'Mi ping es de {ping:.2f}ms')

@bot.tree.command(name='selfping', description='Hace selfping a un usuario')
async def selfping(interaction: discord.Interaction, user: discord.Member):
    if not has_role_or_permission(interaction, 'RolModerador', 'manage_messages'):
        await interaction.response.send_message("No tienes los permisos necesarios para utilizar este comando.", ephemeral=True)
        return
    await interaction.response.send_message(f'{user.mention}', delete_after=0.5)

@bot.tree.command(name='client', description='Asigna el rol de cliente a un usuario')
async def client_command(interaction: discord.Interaction, user: discord.Member):
    role_id = 1159639724407935098
    role = interaction.guild.get_role(role_id)
    
    if role is None:
        await interaction.response.send_message(f'El rol con ID {role_id} no existe en este servidor.', ephemeral=True)
        return
    
    if role in user.roles:
        await interaction.response.send_message(f'El usuario {user.name} ya tiene el rol {role.mention}.', ephemeral=True)
        return
    
    await user.add_roles(role)
    await interaction.response.send_message(f'El usuario {user.name} ha sido asignado al rol {role.mention}.', ephemeral=True)

@bot.tree.command(name='category', description='Cambia la categoría de un canal')
async def category(interaction: discord.Interaction, channel: discord.TextChannel, category: discord.CategoryChannel):
    if not has_role_or_permission(interaction, 'RolModerador', 'manage_channels'):
        await interaction.response.send_message("No tienes los permisos necesarios para cambiar la categoría de un canal.", ephemeral=True)
        return
    try:
        await channel.edit(category=category)
        await interaction.response.send_message(f'El canal {channel.name} ha sido movido a la categoría {category.name}', ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message('No tengo permisos para cambiar la categoría de un canal.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Ocurrió un error: {str(e)}', ephemeral=True)

@bot.tree.command(name='help', description='Muestra la lista de comandos disponibles')
async def help_command(interaction: discord.Interaction):
    commands_info = [
        {
            "name": "about",
            "description": "Información sobre el bot",
            "category": "Información"
        },
        {
            "name": "avatar",
            "description": "Muestra el avatar de un usuario",
            "category": "Usuarios"
        },
        {
            "name": "ban",
            "description": "Banea a un usuario",
            "category": "Moderación"
        },
        {
            "name": "banner",
            "description": "Muestra el banner de un usuario",
            "category": "Usuarios"
        },
        {
            "name": "category",
            "description": "Cambia la categoría de un canal",
            "category": "Administración"
        },
        {
            "name": "client",
            "description": "Asigna el rol de cliente a un usuario",
            "category": "Roles"
        },
        {
            "name": "invite",
            "description": "Genera un enlace de invitación para el bot con los permisos necesarios",
            "category": "Invitaciones"
        },
        {
            "name": "kick",
            "description": "Kickea a un usuario",
            "category": "Moderación"
        },
        {
            "name": "ping",
            "description": "Muestra el ping del bot",
            "category": "Información"
        },
        {
            "name": "purge",
            "description": "Elimina una cantidad de mensajes en un canal",
            "category": "Moderación"
        },
        {
            "name": "selfping",
            "description": "Hace selfping a un usuario",
            "category": "Usuarios"
        },
        {
            "name": "serverinfo",
            "description": "Muestra información del servidor",
            "category": "Información"
        },
        {
            "name": "timeout",
            "description": "Aisla a un usuario",
            "category": "Moderación"
        },
        {
            "name": "userinfo",
            "description": "Muestra información del usuario",
            "category": "Usuarios"
        }
    ]

    embeds = []
    categories = {}

    for command in commands_info:
        category = command["category"] if "category" in command else "General"
        if category not in categories:
            categories[category] = []
        categories[category].append(command)

    for category, commands in categories.items():
        embed = discord.Embed(title=f'Comandos - {category}', color=embed_color)
        embed.set_thumbnail(url=bot.user.avatar.url)

        for command in commands:
            embed.add_field(name=f'/{command["name"]}', value=f'{command["description"]}', inline=True)

        embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, ephemeral=True)

@bot.event
async def on_member_join(member):
    guild = member.guild
    embed = discord.Embed(title=f"¡Bienvenido a {guild.name}, {member.name}!", color=embed_color)
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="**Información de la cuenta**", value=f"Creada el <t:{int(member.created_at.timestamp())}:D>", inline=False)
    embed.add_field(name="**Nuestro servidor**", value=f"Ahora somos {guild.member_count} miembros", inline=False)
    embed.add_field(name="**Mensaje de parte de Moonly**", value="¡Espero que disfrutes tu estadía en nuestro servidor!\n**Recuerda verificarte** para acceder a todos los canales disponibles.", inline=False)
    
    footer = f"{guild.name} • Todos los derechos reservados."
    embed.set_footer(text=footer, icon_url=bot.user.avatar.url)

    channel_id = 1282090206098489395
    channel = bot.get_channel(channel_id)
    if channel is not None:
        await channel.send(embed=embed)

    embed_private = discord.Embed(title=f"¡Bienvenido a {guild.name}, {member.name}!", color=embed_color)
    embed_private.add_field(name="- Recuerda verificarte para ver todos los canales.",value=f"Puedes verificarte en este canal: https://discord.com/channels/1159639252838129704/1159639257388957709", inline=False)
    embed_private.add_field(name="- ¿Necesitas ayuda en alguna compra?",value=f"Abre un ticket después de verificarte para poder ayudarte: https://discord.com/channels/1159639252838129704/1159646450704203821", inline=False)
    embed_private.add_field(name="- ¿Quieres ver todas nuestras redes sociales?",value=f"Puedes encontrarlas aquí: https://linktr.ee/moonlygg", inline=False)
    embed_private.set_thumbnail(url=member.display_avatar.url)
    
    footer_text = f"{guild.name} • Todos los derechos reservados."
    embed_private.set_footer(text=footer_text, icon_url=bot.user.avatar.url)

    await member.send(embed=embed_private)

@bot.event
async def on_member_remove(member):
    guild = member.guild
    embed = discord.Embed(title=f"¡Adiós, {member.name}!", color=embed_color)
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="**Gracias por tu estancia**", value="Esperamos que hayas disfrutado tu tiempo en nuestro servidor.", inline=False)
    embed.add_field(name="**Nuestro servidor**", value=f"Ahora somos {guild.member_count} miembros.", inline=False)

    footer_text = f"{guild.name} • Todos los derechos reservados."
    embed.set_footer(text=footer_text, icon_url=bot.user.avatar.url)

    channel_id = 1159642474445291611
    channel = bot.get_channel(channel_id)
    if channel is not None:
        await channel.send(embed=embed)

bot.run('BOT TOKEN')
