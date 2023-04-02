import requests
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import random
from rich import print
from rich.panel import Panel
import os, sys
import rich.box as box
from rich.status import Status
import webbrowser
import keyboard

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
        
        
class Tracker:
    def __init__(self, Acc_name, time, webhook=None, q_game=False, game_mode=None) -> None:
        #check if mode is given
        self.q_game = q_game
        if self.q_game:
            self.q_inc = 0
            game_mode = game_mode.lower()
            if game_mode == 'rapid':
                self.base = 600
            elif game_mode == 'blitz':
                self.base = 500
            elif game_mode == 'bullet':
                self.base = 60
            
            if game_mode not in ['rapid', 'blitz', 'bullet']:
                print("Error: Invalid game mode")
                print("Please choose custom time and increment")
                self.q_time = input('Time game should last (in seconds) Ex: 600 for rapid: ')
                self.q_inc = input('Increment (in seconds) Ex: 1: to q with 1 second increment: ')
                
            
        
        
        
        if webhook:
            self.webhook = DiscordWebhook(url=webhook)
        else:   
            self.webhook = False
        
        self.name = Acc_name
        self.time = time
        self.old_elo_rapid = 0
        self.old_elo_blitz = 0
        self.old_elo_bullet = 0
        #check if mode is valid
            
        #creating proxy list 
        self.proxy_list = []
        x = requests.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all&simplified=true', stream=True)
        for y in x.iter_lines():
            if y: 
                self.proxy_list.append({'http': f"socks4://{y.decode().strip()}"})
                
        #inititate a simplpromt instance 
        self.simplpromt = simplpromt()
        self.simplpromt.add_to_main("Mint Main")
        self.simplpromt.update(f"Name: [b]{self.name}[/], Check every: [green]{self.time}[/]s")
        

    def give_proxy(self):
        self.choice = random.choice(self.proxy_list)
        return self.choice
        
        
    def choose_check(self, choice):
        #if the choice is rapid then return blitz and bullet
        if choice == 'rapid':
            return ['blitz', 'bullet']
        #if the choice is blitz then return rapid and bullet
        elif choice == 'blitz':
            return ['rapid', 'bullet']
        #if the choice is bullet then return rapid and blitz
        elif choice == 'bullet':
            return ['rapid', 'blitz']
        
        
    def first_contact(self):
        with Status("[bold green]First contact with api initiated...[/]", spinner="dots") as status:
            contact = requests.get(f"https://api.chess.com/pub/player/{self.name}/stats", proxies=self.give_proxy()).json()
            try:
                if contact['code'] == 0:
                    status.update("[bold red]Error: Invalid name[/]")
                    exit()
            except:
                pass
            
            self.old_elo_rapid = contact['chess_rapid']['last']['rating']
            self.old_elo_blitz = contact['chess_blitz']['last']['rating']
            self.old_elo_bullet = contact['chess_bullet']['last']['rating']
            
            
            
            self.simplpromt.update(f" - First contact with api successful")
            
            
            
            renderable = f" Rating in rapid: [green]{contact['chess_rapid']['last']['rating']}[/]\n Rating in blitz: [yellow]{contact['chess_blitz']['last']['rating']}[/]\n Rating in bullet: [red]{contact['chess_bullet']['last']['rating']}[/]"
            
            panel = Panel(
                renderable=renderable,
                title="Current Stats",
                border_style="green",
                width=50,
                height=5,
                expand=False,
                style="bold green",
            )
            
            print(panel)
            
    def Session_Start(self):
        self.first_contact()
        self.simplpromt.update(f" - Session started with {self.name}")
        
        
        while True:
            contact = requests.get(f"https://api.chess.com/pub/player/{self.name}/stats", proxies=self.give_proxy()).json()
            self.current_elo_rapid = contact['chess_rapid']['last']['rating']
            self.current_elo_blitz = contact['chess_blitz']['last']['rating']
            self.current_elo_bullet = contact['chess_bullet']['last']['rating']
        
        
            #Be checking all 3 at the same time
            
            if self.current_elo_rapid > self.old_elo_rapid:
                self.simplpromt.update(f" - [bold green]Rapid[/] elo increased by [bold green]{self.current_elo_rapid - self.old_elo_rapid}[/]")
                self.old_elo_rapid = self.current_elo_rapid
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Rapid elo increased by {self.current_elo_rapid - self.old_elo_rapid}"
                    self.webhook.execute()
                    
            elif self.current_elo_rapid < self.old_elo_rapid:
                self.simplpromt.update(f" - [bold red]Rapid[/] elo decreased by [bold red]{self.old_elo_rapid - self.current_elo_rapid}[/]")
                self.old_elo_rapid = self.current_elo_rapid
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Rapid elo decreased by {self.old_elo_rapid - self.current_elo_rapid}"
                    self.webhook.execute()

            if self.current_elo_blitz > self.old_elo_blitz:
                self.simplpromt.update(f" - [bold green]Blitz[/] elo increased by [bold green]{self.current_elo_blitz - self.old_elo_blitz}[/]")
                self.old_elo_blitz = self.current_elo_blitz
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Blitz elo increased by {self.current_elo_blitz - self.old_elo_blitz}"
                    self.webhook.execute()

            elif self.current_elo_blitz < self.old_elo_blitz:
                self.simplpromt.update(f" - [bold red]Blitz[/] elo decreased by [bold red]{self.old_elo_blitz - self.current_elo_blitz}[/]")
                self.old_elo_blitz = self.current_elo_blitz
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Blitz elo decreased by {self.old_elo_blitz - self.current_elo_blitz}"
                    self.webhook.execute()
                    
            if self.current_elo_bullet > self.old_elo_bullet:
                self.simplpromt.update(f" - [bold green]Bullet[/] elo increased by [bold green]{self.current_elo_bullet - self.old_elo_bullet}[/]")
                self.old_elo_bullet = self.current_elo_bullet
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Bullet elo increased by {self.current_elo_bullet - self.old_elo_bullet}"
                    self.webhook.execute()
                    
            elif self.current_elo_bullet < self.old_elo_bullet:
                self.simplpromt.update(f" - [bold red]Bullet[/] elo decreased by [bold red]{self.old_elo_bullet - self.current_elo_bullet}[/]")
                self.old_elo_bullet = self.current_elo_bullet
                self.queue_game()
                if self.webhook:
                    self.webhook.content = f"Bullet elo decreased by {self.old_elo_bullet - self.current_elo_bullet}"
                    self.webhook.execute()
                    
            #if no change
            if self.current_elo_rapid == self.old_elo_rapid and self.current_elo_blitz == self.old_elo_blitz and self.current_elo_bullet == self.old_elo_bullet:
                self.simplpromt.update(f" - No change in elo, Game in progress?")
                if self.webhook:
                    self.webhook.content = f"No change in elo"
                    self.webhook.execute()

            time.sleep(self.time)
            
    def queue_game(self):
        if self.q_game:
            self.simplpromt.update(f" - Auto queueing game has been enabled, Queueing game...")
            
        
            gen_api = f"https://www.chess.com/play/online/new?action=createLiveChallenge&base={self.base}&timeIncrement={self.q_inc}"
            
            #simulate ctrl + w
            keyboard.press_and_release('ctrl+w')
            #open google
            webbrowser.open_new(gen_api)
            #final step
            time.sleep(2)
            keyboard.press_and_release('ctrl+f5')
        
            
            
#Handler



Name = input("Enter your account name: ")
TimeOut = int(input("Enter the time between each check in seconds: (Dont make it low): "))
discordwebhk = input("Enter your discord webhook (optional) Just press enter to ignore: ")
q_game = input("Do you want to auto queue a game? (y/n): ")
if 'y' in q_game:
    gamemode = input("Enter the gamemode you want to play (rapid/blitz/bullet): ")
    if gamemode not in ['rapid', 'blitz', 'bullet']:
        print("Invalid gamemode, Exiting...")
        exit()
    Tracker(Name, TimeOut, discordwebhk, True, gamemode).Session_Start()
if discordwebhk:
    Tracker(Name, TimeOut, discordwebhk).Session_Start()
else:
    Tracker(Name, TimeOut).Session_Start()

#check if both are valid

    




        
                
                
    
                
        