import feedparser
from bs4 import BeautifulSoup
import datetime
import discord
from datetime import timezone
import dateutil.parser
from dateutil.tz import tzlocal
from discord.ext import commands

def fetch_rss_feed(feed_url):
    try:
        return feedparser.parse(feed_url)
    except Exception as e:
        print(f"Erreur lors de la récupération du flux RSS: {feed_url} - {e}")
        return None

def parse_date(date_string):
    dt = dateutil.parser.parse(date_string)
    local_tz = tzlocal()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)
    else:
        dt = dt.astimezone(local_tz)
    return dt

def filter_articles(feed, keyword, max_age_days):
    if feed is None:
        return []

    filtered_articles = []
    current_time = datetime.datetime.now().replace(tzinfo=None)

    for entry in feed.entries:
        if keyword.lower() in entry.title.lower():
            try:
                published_time = parse_date(entry.published)
                published_time = published_time.replace(tzinfo=None)
                age = current_time - published_time
                if age.days < max_age_days:
                    filtered_articles.append(entry)
            except ValueError:
                print(f"Erreur lors de l'analyse de la date de publication pour {entry.title}. Article ignoré.")

    return filtered_articles


rss_feeds = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/international/rss",
    "https://www.lemonde.fr/rss/une.xml",
    "https://krebsonsecurity.com/feed/",
    "https://www.darkreading.com/rss_simple.asp",
    "https://feeds.feedburner.com/Securityweek",
    "https://nakedsecurity.sophos.com/feed/",
    "https://www.helpnetsecurity.com/feed/",
    "http://feeds.ign.com/ign/games-all",
    "https://www.gamespot.com/feeds/mashup/",
    "https://www.polygon.com/rss/index.xml",
    "https://kotaku.com/rss",
    "https://www.pcgamer.com/rss/",
    "https://www.rockpapershotgun.com/feed",
    "https://www.eurogamer.net/rss",
    "https://www.wired.com/feed/rss",
    "https://www.techradar.com/rss",
    "https://www.zdnet.com/topic/security/rss.xml",
    "https://www.engadget.com/rss.xml",
    "https://www.sciencedaily.com/rss/all.xml",
    "https://www.sciencemag.org/rss/news_current.xml",
    "https://www.space.com/feeds/all",
    "https://www.nature.com/articles.rss",
    "https://www.economist.com/leaders/rss.xml",
    "https://www.ft.com/?format=rss",
    "https://www.bloomberg.com/feed/podcast/etf-iq",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "https://feeds.feedburner.com/entrepreneur/latest",
    "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "https://sports.yahoo.com/mlb/rss.xml",
    "https://rssfeeds.usatoday.com/UsatodaycomSports-TopStories",
    "https://www.si.com/rss/si_topstories.rss",
]


@commands.command(name="recherche")
async def recherche(ctx, *args):
    if not args:
        await ctx.send("Veuillez fournir un mot-clé pour la recherche.")
        return
    await ctx.send("Recherche en cours...")
    
    keyword = " ".join(args)
    max_age_days = 7

    results = []

    for rss_feed in rss_feeds:
        feed = fetch_rss_feed(rss_feed)
        if feed is not None:
            articles = filter_articles(feed, keyword, max_age_days)
            for article in articles[:10]:
                results.append(article)

    if not results:
        await ctx.send(f"Aucun résultat trouvé pour '{keyword}'.")
        return

    results = sorted(results, key=lambda a: parse_date(a.published), reverse=True)[:4]  # Trier et limiter à 4 articles

    for article in results:
        embed = discord.Embed(
            title=article.title,
            url=article.link,
            timestamp=parse_date(article.published),
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_command(recherche)