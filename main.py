import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

secret_role = "luki"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} -   dont use that word!")

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello{ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
    else:
        await ctx.send("role doesnt exist")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
    else:
        await ctx.send("role doesnt exist")

@bot.command()
async def statsclub(ctx):
    await ctx.send("¿Quieres que te ayude a buscar las estadísticas de un club? (si/no)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['si', 'no']

    try:
        respuesta = await bot.wait_for('message', check=check, timeout=30.0)
        if respuesta.content.lower() == 'si':
            await ctx.send("Por favor, introduce el nombre del equipo con el siguiente formato (ej: ca-boca-juniors):")

            def check_equipo(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                nombre_equipo = await bot.wait_for('message', check=check_equipo, timeout=30.0)
                await buscar_estadisticas(ctx, nombre_equipo.content)
            except asyncio.TimeoutError:
                await ctx.send("Tiempo de espera agotado. Por favor, intenta de nuevo.")
        else:
            await ctx.send("No hay problema, si necesitas ayuda, aquí estoy.")
    except asyncio.TimeoutError:
        await ctx.send("Tiempo de espera agotado. Por favor, intenta de nuevo.")

@bot.command()
async def buscar_estadisticas(ctx, equipo: str):
    base_url = f"https://www.fichajes.com/equipo/{equipo.lower().replace(' ', '-')}/estadisticas"
    await ctx.send(f"Buscando estadísticas para '{equipo}'...")

    try:
        pedido_obtenido = requests.get(base_url)
        pedido_obtenido.raise_for_status()
        html_obtenido = pedido_obtenido.text
        soup = BeautifulSoup(html_obtenido, "html.parser")
        divs = soup.find_all('div', class_="goalsStatsByType")
        table_data = []
        goles_area = 0
        goles_fuera_area = 0

        if divs:
            for div in divs:
                text = div.text.strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                # Agrupar las líneas en tríos (Tipo - Porcentaje - Goles)
                for i in range(0, len(lines), 3):
                    if i + 2 < len(lines):
                        descripcion, porcentaje, goles_str = lines[i], lines[i + 1], lines[i + 2]
                        table_data.append((descripcion, porcentaje, goles_str))
                        if "Dentro del área" in descripcion:
                            try:
                                goles_area += int(goles_str)
                            except ValueError:
                                print(f"No se pudo convertir a entero el valor de goles para 'Dentro del área': {goles_str}")
                        elif "Fuera del área" in descripcion:
                            try:
                                goles_fuera_area += int(goles_str)
                            except ValueError:
                                print(f"No se pudo convertir a entero el valor de goles para 'Fuera del área': {goles_str}")
                    elif i < len(lines):
                        row = [lines[i], "", ""]  # Rellena con cadenas vacías si faltan datos
                        if i + 1 < len(lines):
                            row[1] = lines[i + 1]
                        table_data.append(tuple(row))

        total_goles = goles_area + goles_fuera_area

        if table_data:
            table_string = f"**Estadísticas de Goles ({total_goles} Totales) para {equipo}:**\n"
            table_string += "```\n"  # Iniciar de bloque
            table_string += "|         Tipo de Gol         | Porcentaje | Goles |\n"
            table_string += "|-----------------------------|------------|-------|\n"
            for row in table_data:
                description, percentage, goals = row
                table_string += f"| {description:<27} | {percentage:<10} | {goals:<5} |\n"
            table_string += "```"  # Cierre de bloque
            await ctx.send(table_string)
        else:
            await ctx.send(f"No se encontraron estadísticas de goles formateables para '{equipo}'.")

        if not divs: # Ahora verificamos si 'divs' estaba vacío para enviar el otro mensaje
            await ctx.send(f"No se encontraron secciones de estadísticas de goles para '{equipo}'.")

    except requests.exceptions.RequestException as e:
        await ctx.send(f"Hubo un error al acceder a la página: {e}")
    except Exception as e:
        await ctx.send(f"Ocurrió un error durante el procesamiento: {e}")

@bot.command()
async def dolarblue(ctx):
    url = "https://dolarapi.com/v1/dolares/blue"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        fecha_actualizacion_str = data.get("fechaActualizacion")
        fecha_formateada = ""
        if fecha_actualizacion_str:
            fecha_formateada = datetime.fromisoformat(fecha_actualizacion_str.replace('Z', '+00:00')).strftime('%Y-%m-%d') # Solo la fecha
        compra = data.get("compra")
        venta = data.get("venta")

        tabla = "```\n"
        tabla += "Información del Dólar Blue \n"
        tabla += "+--------------------------+--------+--------+\n"
        tabla += "| Fecha de Actualización   | Compra | Venta  |\n"
        tabla += "+--------------------------+--------+--------+\n"
        tabla += f"| {fecha_formateada:<24} | ${compra:<6}| ${venta:<6}|\n"
        tabla += "+--------------------------+--------+--------+\n"
        tabla += "```"
        await ctx.send(tabla)

        print("Información del Dólar Blue (Consola):")
        print(f"Fecha de Actualización: {fecha_formateada}") # Solo la fecha
        print(f"Compra: ${compra}")
        print(f"Venta: ${venta}")

    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al obtener la información del dólar blue: {e}")
        print(f"Error al obtener la información del dólar blue (Consola): {e}")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al procesar la información del dólar blue: {e}")
        print(f"Ocurrió un error al procesar la información del dólar blue (Consola): {e}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)