import json
from datetime import timezone,datetime, timedelta
import feedparser
from discord.ext import tasks

#Changez l'id de votre Channel
CHANNEL_ID_SECU = 1091763254

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
        if (datetime.now(timezone.utc) - datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")) >= timedelta(days=14):
            return False
        else:
            return True
    else:
        return False

@tasks.loop(minutes=30)
async def fetch_articles(bot):
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
        if (datetime.now(timezone.utc) - datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")) >= timedelta(days=14):
            del published_articles[link]

    save_published_articles(published_articles)