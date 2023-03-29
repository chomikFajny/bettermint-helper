import requests
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import random
from rich import print
from rich.panel import Panel
import os, sys
import rich.box as box



class simplpromt():
    def __init__(self, custom_promt=None, Defaults=True) -> None:
        #clear cmd
        username = os.getlogin()
        self.username =  f'[blue]{username}[/]'
        
        self.control_panel = Panel
        self.instace = Panel
        
        current_path = os.getcwd()
        #format path
        current_path = current_path.replace('\\', '/')
        #remove D:
        self.current_path = current_path[2:]
        
        
        self.osx = sys.platform
        
        self.osxversion = sys.version
        
        self.sizes = os.get_terminal_size()
        
        
        
        if custom_promt:
            self.custom_promt = custom_promt
        else:
            self.old_promt = f"[green]Mint@[/]{self.username}: {self.current_path} $"
            self.custom_promt = f"[green]Mint@[/]{self.username}: {self.current_path} $"
        
        self.newnum = self.sizes[0]-len(self.custom_promt) if len(self.custom_promt)< self.sizes[0]/2 else self.sizes[0]*2
        
        if Defaults:
            print((self.instace(f"{self.custom_promt} \n[gray7]OS: {self.osx} {self.osxversion}[/] $", height=4, width=self.sizes[0]-self.newnum , border_style='grey39', box=box.HORIZONTALS)))

        
    def clear():
        def cls(func):
            def wrapper(*args, **kwargs):
                os.system('cls' if os.name == 'nt' else 'clear')
                func(*args, **kwargs)
            return wrapper
        return  cls
    

    @clear()
    def add_to_main(self, text, cls_previous=False):
        if cls_previous:
            self.custom_promt = self.old_promt
        self.custom_promt += f' {text}'
        
        print((self.instace(self.custom_promt, height=3, width=self.sizes[0]-self.newnum, border_style='grey39', box=box.HORIZONTALS)))
        

    def update(self, text):
        print(f"  {text}")

#proxies.txt is a file of socks5 proxies in the format of ip:port (one per line) extract them into a dict
proxies = {}
with open("proxies.txt", "r") as f:
    for line in f:
        line = line.strip()
        ip, port = line.split(":")
        proxies[ip] = port

name = input("name: ")
timein = int(input("time of waiting till sending (seconds): "))
webhookin = input("webhook link: ")
mode = input("enter mode that u play play on: ")
webhook = DiscordWebhook(url=webhookin)

#Panel Profit
panel_profit_title = "Profit"
panel_profit_color = "green"
#Panel Lose 
panel_lose_title = "Lose"
panel_lose_color = "red"
#Panel Neutral
panel_neutral_title = "-x-"
panel_neutral_color = "yellow"

simpl = simplpromt()



oldstat = requests.get(f"https://api.chess.com/pub/player/{name}/stats").json()
#mode selector
mode = mode.lower()
if mode == 'bullet':
    oldstat1 = oldstat["chess_bullet"]
elif mode == 'blitz':
    oldstat1 = oldstat["chess_blitz"]
elif mode == 'rapid':    
    oldstat1 = oldstat["chess_rapid"] # or chess_rapid or chess_blitz
oldstat2 = oldstat1["last"]
oldelo = oldstat2["rating"]
started = DiscordEmbed(title='Started', description=f'Started with ``{oldelo}`` elo', color='808080')
webhook.add_embed(started)
response = webhook.execute(remove_embeds=True)




# print(Panel(
#     renderable=f"Started with {oldelo} elo",
#     title="BetterMintHelper",
#     title_align="center",
#     border_style="green",
#     padding=(1, 1),
#     expand=False,
#     style="bold",
#     width=30,
#     height=5,
# ))



while True:
    proxy = random.choice(list(proxies.keys()))
    use_proxy = {'http': f"socks5://{proxy}:{proxies[proxy]}"}
    simpl.update(f"Name: [b]{name}[/], Time: [green]{timein}[/], Proxy: [blue]{proxy}[/]:[red]{proxies[proxy]}[/], Mode: [yellow]{mode}[/]")

    time.sleep(timein)
    stat = requests.get(f"https://api.chess.com/pub/player/{name}/stats", proxies=use_proxy).json()
    stat1 = stat["chess_bullet"] # or chess_rapid or chess_blitz
    stat2 = stat1["last"]
    elo = stat2["rating"]
    if elo >= oldelo:
        e_change = elo - oldelo
        wonweb = DiscordEmbed(title='Profit', description=f'Gain ``+{e_change}`` points\nNew elo: ``{elo}``', color='00ff00')
        webhook.add_embed(wonweb)
        print("profit!")
        e_change = elo - oldelo
        print(Panel(
            renderable=f"Account: {name}\nELO: {elo} (+{e_change})",
            title="BetterMintHelper",
            title_align="center",
            border_style="green",
            expand=False,
            style="bold",
            width=30,
            height=5,
        ))
        
        response = webhook.execute(remove_embeds=True)
        oldelo = elo
        
    else:
        e_change = oldelo - elo
        lostweb = DiscordEmbed(title='Lose', description=f'Lost ``-{e_change}`` points\nNew elo: ``{elo}``', color='FF0000')
        webhook.add_embed(lostweb)
        print(Panel(
            renderable=f"Account: {name}\nELO: {elo} (-{e_change})",
            title="BetterMintHelper",
            title_align="center",
            border_style="red",
            expand=False,
            style="bold",
            width=30,
            height=5,
        ))
        response = webhook.execute(remove_embeds=True)
        oldelo = elo
        
