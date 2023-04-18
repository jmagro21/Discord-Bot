from encrypt_decrypt import generate_key, encrypt_data

key = generate_key()

discord_token = '' #Mettez votre Token ici

encrypted_discord_token = encrypt_data(discord_token, key)

with open('discord_token.enc', 'wb') as enc_file:
    enc_file.write(encrypted_discord_token)

with open('keyToken.key', 'wb') as key_file:
    key_file.write(key)
