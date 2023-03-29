import requests
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

name = input("name: ")
timein = int(input("time of waiting till sending (seconds): "))
webhookin = input("webhook link: ")
webhook = DiscordWebhook(url=webhookin)


oldstat = requests.get(f"https://api.chess.com/pub/player/{name}/stats").json()
oldstat1 = oldstat["chess_bullet"] # or chess_rapid or chess_blitz
oldstat2 = oldstat1["last"]
oldelo = oldstat2["rating"]
started = DiscordEmbed(title='Started', description=f'Started with ``{oldelo}`` elo', color='808080')
webhook.add_embed(started)
response = webhook.execute(remove_embeds=True)

print("starting!")
while True:
    time.sleep(timein)
    stat = requests.get(f"https://api.chess.com/pub/player/{name}/stats").json()
    stat1 = stat["chess_bullet"] # or chess_rapid or chess_blitz
    stat2 = stat1["last"]
    elo = stat2["rating"]
    if elo >= oldelo:
        e_change = elo - oldelo
        wonweb = DiscordEmbed(title='Profit', description=f'Gain ``+{e_change}`` points\nNew elo: ``{elo}``', color='00ff00')
        webhook.add_embed(wonweb)
        print("profit!")
        e_change = elo - oldelo
        print(f"+{e_change}")
        response = webhook.execute(remove_embeds=True)
        oldelo = elo
    else:
        e_change = oldelo - elo
        lostweb = DiscordEmbed(title='Lose', description=f'Lost ``-{e_change}`` points\nNew elo: ``{elo}``', color='FF0000')
        webhook.add_embed(lostweb)
        print("lose")
        print(f"-{e_change}")
        response = webhook.execute(remove_embeds=True)
        oldelo = elo
        