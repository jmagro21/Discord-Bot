def setup(bot) :
    bot.remove_command("help")

    @bot.command(name="help")
    async def help(ctx):
        if ctx.guild is not None:
            await ctx.author.send("Veuillez utiliser cette commande en message privé.")
            return
        else:
            await ctx.send("""
                        -help : Pour afficher les options (à utiliser en message privé)
-cve : Afficher les cve de la journée
-cvesemaine : Afficher toutes les cve de la semaine
-film : Affiche les films du dossier
-recherche : Affiche les derniers articles avec vos mots clefs
-cverecherche : Affiche des cve selons des options a vous /!\ elles sont en anglais et pas forcément validée. (Option disponible après : Recherche Général, par produit, par Fabriquant et par CVE)
""")