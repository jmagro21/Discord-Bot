import requests
import csv
from bs4 import BeautifulSoup
import datetime
from datetime import datetime
import discord

fields = ['titre', 'score', 'conf_impact', 'conf_desc', 'integ_impact', 'integ_desc', 'avail_impact', 'avail_desc', 'access_complexity', 'access_desc', 'auth_required', 'auth_desc', 'ga']
data_list = []
stop = 0

async def envoiemessage(ctx, message):
    await ctx.send(message)

def forgeURL(scoremin, scoremax, annee, mois, page):
    url = "/vulnerability-list.php?vendor_id=0&product_id=0&version_id=0&page=" + str(page) + "&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=" + str(scoremin) + "&cvssscoremax=" + str(scoremax) + "&year=" + str(annee) + "&month=" + str(mois) + "&cweid=0&order=1"
    return url

def analyse(rows, titre):
    score = ''
    conf_impact = ''
    conf_desc = ''
    integ_impact = ''
    integ_desc = ''
    avail_impact = ''
    avail_desc = ''
    access_complexity = ''
    access_desc = ''
    auth_required = ''
    auth_desc = ''
    ga = ''
    for row in rows:
        th = row.find("th")
        if th:
            if th.text == "CVSS Score":
                score_element = row.find("div", class_="cvssbox")
                score = score_element.text
            elif th.text == "Confidentiality Impact":
                conf_element = row.find("td")
                conf_impact = conf_element.find("span", style=True)
                conf_desc = conf_element.find("span", class_="cvssdesc")
                if conf_impact is not None:
                    conf_impact = conf_impact.text
                    conf_desc = conf_desc.text
            elif th.text == "Integrity Impact":
                integ_element = row.find("td")
                integ_impact = integ_element.find("span", style=True)
                integ_desc = integ_element.find("span", class_="cvssdesc")
                if integ_impact is not None:
                    integ_impact = integ_impact.text
                    integ_desc = integ_desc.text
            elif th.text == "Availability Impact":
                avail_element = row.find("td")
                avail_impact = avail_element.find("span", style=True)
                avail_desc = avail_element.find("span", class_="cvssdesc")
                if avail_impact is not None:
                    avail_impact = avail_impact.text
                    avail_desc = avail_desc.text
            elif th.text == "Access Complexity":
                access_element = row.find("td")
                access_complexity = access_element.find("span", style=True)
                access_desc = access_element.find("span", class_="cvssdesc")
                if access_desc is not None:
                    access_complexity = access_complexity.text
                    access_desc = access_desc.text
            elif th.text == "Authentication":
                auth_element = row.find("td")
                auth_required = auth_element.find("span", style=True)
                auth_desc = auth_element.find("span", class_="cvssdesc")
                if auth_required is not None:
                    auth_required = auth_required.text
                    auth_desc = auth_desc.text
            elif th.text == "Gained Access":
                ga_element = row.find("td")
                ga = ga_element.find("span", style=True).text
    data_list.append({'titre': titre, 'score': score, 'conf_impact': conf_impact, 'conf_desc': conf_desc, 'integ_impact': integ_impact, 'integ_desc': integ_desc, 'avail_impact': avail_impact, 'avail_desc': avail_desc, 'access_complexity': access_complexity, 'access_desc': access_desc, 'auth_required': auth_required, 'auth_desc': auth_desc, 'ga': ga})
    return data_list

async def scrapping(url2, ctx):
    response2 = requests.get(url2)
    html_content2 = response2.content
    soup2 = BeautifulSoup(html_content2, 'html.parser')
    titre = soup2.title.string
    await envoiemessage(ctx, titre)
    table = soup2.find("table", id="cvssscorestable")
    if table:  # Ajoutez cette vérification
        rows = table.find_all("tr")
        analyse(rows, titre)
    else:
        print(f"Table with ID 'cvssscorestable' not found in {url2}")


async def principal(ctx, user_id):
    page = 1
    shastr = ""
    now = datetime.now()
    mois = now.month
    while page != 2:
        url = forgeURL(0, 10, 2023, mois, page)
        response = requests.get("https://www.cvedetails.com" + url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a', href=True):
            if a['href'].startswith(url):
                shastr = a['href']
        url = "https://www.cvedetails.com" + shastr
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        page = page + 1
        for a in soup.find_all('a', href=True):
            if a['href'].startswith("/cve/CVE"):
                url2 = "https://www.cvedetails.com" + a['href']
                await scrapping(url2, ctx)
    await save(ctx, user_id)

async def reFab(fabriquant, ctx, user_id):
    url = "https://www.cvedetails.com/vendor-search.php?search=" + fabriquant
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a', href=True):
        if a['href'].startswith("/vulnerability-list/vendor_id"):
            url2 = "https://www.cvedetails.com" + a['href']
            response = requests.get(url2)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            for a in soup.find_all('a', href=True):
                if a['href'].startswith("/cve/CVE"):
                    url3 = "https://www.cvedetails.com" + a['href']
                    await scrapping(url3, ctx)
    await save(ctx, user_id)

async def reEquipement(equipement, ctx, user_id):
    url = "https://www.cvedetails.com/product-search.php?search=" + equipement
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a', href=True):
        if a['href'].startswith("/vulnerability-list/vendor_id"):
            url2="https://www.cvedetails.com"+a['href']
            response = requests.get(url2)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            for a in soup.find_all('a', href=True):
                if a['href'].startswith("/cve/CVE"):
                    url3="https://www.cvedetails.com"+a['href']
                    await scrapping(url3,ctx)
    await save(ctx, user_id)

async def reCVE(cve,ctx,user_id) : 
    url2 = "https://www.cvedetails.com/cve-details.php?t=1&cve_id="+cve
    await envoiemessage(ctx, url2)
    await scrapping(url2,ctx)
    await save(ctx, user_id)
    
async def save(ctx, user_id):
    file_name = str(user_id) + ".csv"
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
    
    user = ctx.author
    await user.send("Voici La liste de vos CVE :", file=discord.File(file_name))

def setup(bot) :
    @bot.command(name="cverecherche")
    async def cve_recherche(ctx):
        user_id = ctx.author.id
        def check_author(m):
            return m.author == ctx.author
            
        await ctx.send("Que souhaitez-vous rechercher ? (general/produit/Fabriquant/cve)")
        choice = await bot.wait_for('message', check=check_author)
        
        if choice.content.lower() == 'general':
            await general_script(ctx,user_id)

        elif choice.content.lower() == 'produit':
            await ctx.send("Quel type de produit cherchez vous ? : ")
            product = await bot.wait_for('message', check=check_author)
            await produit_script(ctx, product,user_id)

        elif choice.content.lower() == 'Fabriquant':
            await ctx.send("Quel type de Fabriquant cherchez vous ? : ")
            fabriquant = await bot.wait_for('message', check=check_author)
            await fabriquant_script(ctx,fabriquant,user_id)

        elif choice.content.lower() == 'cve':
            await ctx.send("Veuille indiquer la CVE que vous recherchez (match : CVE-2023-25168) : ")
            cve = await bot.wait_for('message', check=check_author)
            await cve_script(ctx,cve,user_id)
        else:
            await ctx.send("Choix invalide. Veuillez recommencer.")

    async def general_script(ctx,user_id):
        await ctx.send("Recherche des dernières cve...")
        await principal(ctx,user_id)

    async def produit_script(ctx, product,user_id):
        await ctx.send("Recherche des CVE sur le produit : " + product.content  +"...")
        await reEquipement(product.content , ctx,user_id)

    async def fabriquant_script(ctx,fabriquant,user_id):
        await ctx.send("Recherche des CVE sur le fabriquant : " + fabriquant.content  +"...")
        await reFab(fabriquant.content ,ctx,user_id)

    async def cve_script(ctx, cve,user_id):
        await ctx.send("Recherche de la : " + cve.content  + "...")
        await reCVE(cve.content , ctx,user_id)