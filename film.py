import os
import json
import datetime
from datetime import datetime
from discord.ext import tasks

#Modifier l'ID de votre channel
CHANNEL_ID = 10903514858

#Changez votre chemin absolu
MONITORED_FOLDER = "film"

def load_previous_files():
    if os.path.exists("data/data.json"):
        with open("data/data.json", "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    else:
        files = {f: datetime.now().strftime("%Y-%m-%d") for f in os.listdir(MONITORED_FOLDER) if os.path.isfile(os.path.join(MONITORED_FOLDER, f))}
        save_previous_files(files)
        return files

def save_previous_files(files):
    with open("data/data.json", "w") as f:
        json.dump(files, f)
        

async def send_new_files(new_files, bot):
    channel = bot.get_channel(CHANNEL_ID)
    for file in new_files.items():
        await channel.send(f"Upload de nouveau film : {file}")

async def check_new_files(bot):
    previous_files = load_previous_files()
    current_files = {f: datetime.now().strftime("%Y-%m-%d") for f in os.listdir(MONITORED_FOLDER) if os.path.isfile(os.path.join(MONITORED_FOLDER, f))}

    new_files = {file: date for file, date in current_files.items() if file not in previous_files}

    if new_files:
        await send_new_files(new_files,bot)
        previous_files.update(new_files)
        save_previous_files(previous_files)

@tasks.loop(minutes=30)
async def check_files_loop(bot):
    await check_new_files(bot)
    
def setup(bot) :
    @bot.command(name="film")
    async def film(ctx):
        files = load_previous_files()
        if files:
            response = "Liste des films :\n"
            for f, date in files.items():
                file_line = f"- {f} (ajouté le {date})\n"
                if len(response + file_line) > 2000:
                    await ctx.send(response)
                    response = file_line
                else:
                    response += file_line
            await ctx.send(response)
        else:
            await ctx.send("Aucun film n'a été trouvé.")
        

