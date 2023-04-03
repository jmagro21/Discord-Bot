import os
import discord
import feedparser
import json
import datetime
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

TOKEN = "Nzc5Mzk3MTY3MjQ4ODM0NTcx.Gtnx7I.TqlSyW3djn6vsijfNRRJ35q6Yq3elxd9exQk2Y"

CHANNEL_ID_SECU = 1091763254675648604

RSS_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"

JSON_FILE = "data/published_articles.json"

def load_published_articles():
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_published_articles(articles):
    with open(JSON_FILE, "w") as f:
        json.dump(articles, f)

def is_article_published(article, published_articles):
    if article.link in published_articles:
        pub_date = published_articles[article.link]
        if (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")).days >= 7:
            return False
        else:
            return True
    else:
        return False

@bot.event
async def on_ready():
    print("Le bot est connecté")
    fetch_articles.start()  # Démarrer la boucle pour vérifier les articles

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
        if (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")).days >= 7:
            del published_articles[link]

    save_published_articles(published_articles)


# Utiliser le TOKEN chargé précédemment
bot.run(TOKEN)
