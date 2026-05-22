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

    def joinHandle(self):
        pass

    def randName(self, integer):
        return ''.join(random.choice(string.ascii_letters) for _ in range(integer))

    def joingame(self):
        # Generate bot username
        if self.custom_user == "":
            self.username = ('xeny ' + '| ' + self.randName(6))
        else:
            self.username = (self.custom_user + ' | ' + self.randName(6))

        # Create a new client instance for each bot
        bot = client()
        
        try:
            bot.join(self.gamepin, self.username)
            bot.on("joined", self.joinHandle)
            
            with self.lock:
                self.successful_joins += 1
                print(f"[{self.successful_joins}/{self.botamount}] Joined with username: {self.username}")
                
        except Exception as e:
            with self.lock:
                self.failed_joins += 1
                print(f"Failed to join with {self.username}: {e}")

        # Small delay to prevent rate limiting
        time.sleep(0.1)

if __name__ == '__main__':
    Client = KahootSpammer()
    
    print(f"\nStarting {Client.botamount} bots...")
    print("-" * 40)
    
    threads = []
    for x in range(int(Client.botamount)):
        # Fixed: Pass the method reference, not the result
        thread = threading.Thread(target=Client.joingame)
        threads.append(thread)
        thread.start()
        time.sleep(0.05)  # Stagger thread starts
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("-" * 40)
    print(f"Finished! Successfully joined: {Client.successful_joins}, Failed: {Client.failed_joins}")
