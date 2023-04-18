import os
import json
import discord
from discord.ext import tasks
from datetime import datetime, date
import feedparser 

RSS_URL = "https://www.cert.ssi.gouv.fr/feed/"

#Modifier l'ID de votre Channel
CVE_CHANNEL_ID = 1090706547

def load_cve_data():
    if os.path.exists("data/cve.json"):
        try:
            with open("data/cve.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"date": "", "cves": {}}
    return {"date": "", "cves": {}}

def save_cve_data(data):
    with open("data/cve.json", "w") as f:
        json.dump(data, f)

async def display_cve(entry, channel):
    embed = discord.Embed(
        title=entry.title,
        description=entry.summary,
        url=entry.link,
        color=discord.Color.red()
    )
    await channel.send(embed=embed)

def days_between_dates(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d").date()
    d2 = datetime.strptime(date2, "%Y-%m-%d").date()
    delta = d2 - d1
    return delta.days

@tasks.loop(minutes=60)
async def check_cve(bot):
    channel = bot.get_channel(CVE_CHANNEL_ID)
    if not channel:
        return
    cve_data = load_cve_data()
    today = str(date.today())
    if cve_data["date"] != today:
        cve_data["date"] = today
    cve_data["cves"] = {cve_id: cve_date for cve_id, cve_date in cve_data["cves"].items()
                        if days_between_dates(cve_date, today) <= 14}
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        if entry.id not in cve_data["cves"]:
            cve_data["cves"][entry.id] = today
            save_cve_data(cve_data)
            
            await display_cve(entry, channel)
            
def setup(bot) :
    @check_cve.before_loop
    async def before_check_cve():
        await bot.wait_until_ready()
    
    @bot.command(name="cvesemaine")
    async def show_cve_semaine(ctx):
        if ctx.guild is not None:
            await ctx.author.send("Veuillez utiliser cette commande en message privé.")
            return

        cve_data = load_cve_data()
        cves = cve_data["cves"]
        today = str(date.today())

        if not cves:
            await ctx.send("Aucune CVE pour cette semaine.")
        else:
            feed = feedparser.parse(RSS_URL)
            entries_by_id = {entry.id: entry for entry in feed.entries}
            for cve_id, cve_date in cves.items():
                if days_between_dates(cve_date, today) <= 7:
                    entry = entries_by_id.get(cve_id)
                    if entry:
                        await display_cve(entry, ctx)
                        
    @bot.command(name="cve")
    async def show_cve(ctx):
        if ctx.guild is not None:
            await ctx.author.send("Veuillez utiliser cette commande en message privé.")
            return

        cve_data = load_cve_data()
        cves = cve_data["cves"]

        if not cves:
            await ctx.send("Aucune CVE pour aujourd'hui.")
        else:
            feed = feedparser.parse(RSS_URL)
            entries_by_id = {entry.id: entry for entry in feed.entries}
            today = datetime.today().strftime("%Y-%m-%d")

            cves_today = {cve_id: date for cve_id, date in cves.items() if date == today}

            if not cves_today:
                await ctx.send("Aucune CVE pour aujourd'hui.")
            else:
                for cve_id in cves_today:
                    entry = entries_by_id.get(cve_id)
                    if entry:
                        await display_cve(entry, ctx)
                    
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        await bot.process_commands(message)