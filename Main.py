import discord
from discord.ext import commands
from encrypt_decrypt import decrypt_data

import botrecherche
import film
import newscve
import help
import newscyber
import cvere

def get_discord_token():
    # Chargez la clé de chiffrement
    with open('keyToken.key', 'rb') as key_file:
        key = key_file.read()

    # Chargez et déchiffrez le token du bot Discord
    with open('discord_token.enc', 'rb') as enc_file:
        encrypted_discord_token = enc_file.read()
        decrypted_discord_token = decrypt_data(encrypted_discord_token, key)

    return decrypted_discord_token

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Gestion d'erreur
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass  # Ignore l'erreur si la commande n'est pas trouvée
    else:
        raise error  # Lève l'erreur pour les autres types d'erreurs

# quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    await newscve.check_cve.start(bot)
    await film.check_files_loop.start(bot)
    await newscyber.fetch_articles.start(bot)


botrecherche.setup(bot)
film.setup(bot)
newscve.setup(bot)
help.setup(bot)
cvere.setup(bot)

bot.run(get_discord_token())