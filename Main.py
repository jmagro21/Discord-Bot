import os
import discord
import json
import time
import datetime
from discord.ext import commands, tasks
import feedparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timezone, timedelta, date

#--------------------------------------------------------------------------------------------------
# Initialisation !!!

# Remplacez "YOUR_DISCORD_BOT_TOKEN" par le token de votre bot
TOKEN = "Votre Token"
# URL du flux RSS des dernières CVE en français
RSS_URL = "https://www.cert.ssi.gouv.fr/feed/"
# URL flux news cyber
RSS_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"
# ID du channel où seront envoyées les mises à jour CVE
CVE_CHANNEL_ID = "Id de votre channel"
# ID du channel où seront envoyées les notifications de nouveaux fichiers
CHANNEL_ID = "Id de votre channel"
# ID du channel pour la sécurité informatique
CHANNEL_ID_SECU = "Id de votre channel"
# Fichier de gestion des dernières nouveautés dans votre dossier
FICHIER = "Fichier.json"
# Fichier pour vos CVE
CVE = "Cve.json"
LASTCVE = "LastCve.json"
# Fichier de gestion des derniers articles cyber
ARTICLE_SECU = "Article_Secu.json"
# Dossier surveillé
MONITORED_FOLDER = "Liens de votre dossier à vérifier ex : c:\\test"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# Liste des CVE déjà affichées
displayed_cves = []
#--------------------------------------------------------------------------------------------------
# Partie de gestion des fichiers
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, previous_files):
        self.previous_files = previous_files

    async def on_created(self, event):
        if datetime.now().hour >= 19:
            new_file = os.path.basename(event.src_path)
            if new_file not in self.previous_files:
                self.previous_files.append(new_file)
                save_previous_files(self.previous_files)

                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f"Upload de nouveau fichier : {new_file}")

def load_previous_files():
    if os.path.exists(FICHIER):
        with open(FICHIER, "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    else:
        files = [f for f in os.listdir(MONITORED_FOLDER) if os.path.isfile(os.path.join(MONITORED_FOLDER, f))]
        save_previous_files(files)
        return files

def save_previous_files(files):
    with open(FICHIER, "w") as f:
        json.dump(files, f)

# Renvoi un msg privée après l'utilisation du !fichier en msg au bot
@bot.command(name="fichier")
async def film(ctx):
    files = load_previous_files()
    if files:
        response = "Liste des fichiers :\n"
        for f in files:
            if len(response + f"- {f}\n") > 2000:
                await ctx.send(response)
                response = f"- {f}\n"
            else:
                response += f"- {f}\n"
        await ctx.send(response)
    else:
        await ctx.send("Aucun fichier n'a été trouvé.")

#--------------------------------------------------------------------------------------------------
# Partie de gestion de CVE
def load_cve_data():
    if os.path.exists(CVE):
        try:
            with open(CVE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Si une erreur JSON est détectée, renvoie un dictionnaire par défaut
            return {"date": "", "cves": {}}
    return {"date": "", "cves": {}}

def save_cve_data(data):
    with open(CVE, "w") as f:
        json.dump(data, f)

def load_displayed_cves():
    if os.path.exists(LASTCVE):
        try:
            with open(LASTCVE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Si une erreur JSON est détectée, renvoie une liste vide
            return {"date": "", "cves": {}}
    return {"date": "", "cves": {}}

def save_displayed_cves(cves, today):
    with open(LASTCVE, "w") as f:
        f.write("")  # Vide le fichier avant d'ajouter de nouvelles données

    data = {"date": today, "cves": cves} 
    with open(LASTCVE, "w") as f:
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

@tasks.loop(minutes=60)  # Vérifie les nouvelles CVE toutes les heures
async def check_cve():
    channel = bot.get_channel(CVE_CHANNEL_ID)
    if not channel:
        return

    cve_data = load_cve_data()
    today = str(date.today())

    if cve_data["date"] != today:
        cve_data["date"] = today

    # Filtrer les CVE dont la date est inférieure ou égale à 7 jours
    cve_data["cves"] = {cve_id: cve_date for cve_id, cve_date in cve_data["cves"].items()
                        if days_between_dates(cve_date, today) <= 7}

    feed = feedparser.parse(RSS_URL)
    displayed_cves = load_displayed_cves()

    for entry in feed.entries:
        if entry.id not in cve_data["cves"]:
            cve_data["cves"][entry.id] = today
            save_cve_data(cve_data)

            if entry.id not in displayed_cves:
                displayed_cves[entry.id] = today
                save_displayed_cves(displayed_cves, today)

            await display_cve(entry, channel)

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
                
@check_cve.before_loop
async def before_check_cve():
    await bot.wait_until_ready()
    
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
    
#--------------------------------------------------------------------------------------------------
#Partie de Gestion des news Cyber
def load_published_articles():
    try:
        with open(ARTICLE_SECU, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_published_articles(articles):
    with open(ARTICLE_SECU, "w") as f:
        json.dump(articles, f)

def is_article_published(article, published_articles):
    if article.link in published_articles:
        pub_date = published_articles[article.link]
        if (datetime.now(timezone.utc) - datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")) >= timedelta(days=7):
            return False
        else:
            return True
    else:
        return False

@tasks.loop(minutes=30)
async def fetch_articles():
    published_articles = load_published_articles()
    feed = feedparser.parse(RSS_FEED_URL)

    break_loop = False
    for entry in feed.entries:
        if break_loop:
            break

        if is_article_published(entry, published_articles):
            break_loop = True
            continue

        channel = bot.get_channel(CHANNEL_ID_SECU)
        message = f"{entry.link} (publié sur {entry.published})"
        await channel.send(message)
        published_articles[entry.link] = entry.published

    for link, pub_date in list(published_articles.items()):
        if (datetime.now(timezone.utc) - datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")) >= timedelta(days=7):
            del published_articles[link]

    save_published_articles(published_articles)
#-------------------------------------------------------------------------------------------------
#Gestion d'erreur
@bot.event        
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass  # Ignore l'erreur si la commande n'est pas trouvée
    else:
        raise error  # Lève l'erreur pour les autres types d'erreurs
    
#-------------------------------------------------------------------------------------------------
# !help
bot.remove_command("help")

@bot.command(name="help")
async def help(ctx):
    if ctx.guild is not None:
        await ctx.author.send("Veuillez utiliser cette commande en message privé.")
        return
    else:
        await ctx.send("""
                       -help : Pour afficher les options (à utiliser en message privé)
-cve : Afficher les dernières cve
-cvesemaine : Afficher toutes les cve de la semaine
-fichier : Affiche les fichiers du serveur
""")
                       
#--------------------------------------------------------------------------------------------------
# Fonction Principal, pour faire tout tourner
@bot.event
async def on_ready():
    print(f'{bot.user} est connecté')
    check_cve.start()

    # Initialisation du gestionnaire de fichiers
    print(f"Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})")
    previous_files = load_previous_files()

    observer = Observer()
    event_handler = NewFileHandler(previous_files)
    observer.schedule(event_handler, MONITORED_FOLDER, recursive=False)
    observer.start()
    
    fetch_articles.start()  # Démarrer la boucle pour vérifier les articles
#--------------------------------------------------------------------------------------------------
bot.run(TOKEN)
