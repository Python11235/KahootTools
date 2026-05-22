import string, random, os, time, threading
from kahoot import client

class KahootSpammer:
    def __init__(self):
        print('KahootTools - Remastered by Nightmrs - Originally made by xeny')
        self.gamepin = input('PIN: ')
        self.botamount = input('Amount of bots (max 2000): ')
        self.custom_user = input('Enter desired username (5 or less chars) (leave blank if none): ')
        self.successful_joins = 0
        self.failed_joins = 0
        self.lock = threading.Lock()
        self.joined_bots = []

    def joinHandle(self, data=None):
        with self.lock:
            self.successful_joins += 1
            self.joined_bots.append(self.current_username)
            print(f"[{self.successful_joins}] Joined: {self.current_username}")

    def randName(self, integer):
        return ''.join(random.choice(string.ascii_letters) for _ in range(integer))

    def joingame(self):
        if self.custom_user == "":
            self.current_username = ('xeny ' + '| ' + self.randName(6))
        else:
            self.current_username = (self.custom_user + ' | ' + self.randName(6))

        bot = client()
        
        try:
            bot.on("joined", self.joinHandle)
            bot.join(self.gamepin, self.current_username)
            time.sleep(3)  # Wait for connection
            
        except Exception as e:
            with self.lock:
                self.failed_joins += 1
                print(f"Failed: {self.current_username} - {e}")

if __name__ == '__main__':
    Client = KahootSpammer()
    
    print(f"\nGame PIN: {Client.gamepin}")
    print(f"Bots: {Client.botamount}")
    print(f"Username prefix: {'xeny' if Client.custom_user == '' else Client.custom_user}")
    print("\nConfirm? (y/n): ", end="")
    
    if input().lower() != 'y':
        print("Cancelled.")
        exit()
    
    print(f"\nStarting {Client.botamount} bots...")
    print("-" * 40)
    
    threads = []
    for x in range(int(Client.botamount)):
        thread = threading.Thread(target=Client.joingame)
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Stagger starts
    
    for thread in threads:
        thread.join()
    
    print("-" * 40)
    print(f"Done! Joined: {Client.successful_joins} | Failed: {Client.failed_joins}")
