import string
import random
import time
import threading
import asyncio
from kahoot import KahootClient


class KahootSpammer:
    def __init__(self):
        print('KahootTools - Remastered by Nightmrs - Originally made by xeny')
        self.gamepin = int(input('PIN: '))
        self.botamount = input('Amount of bots (max 2000): ')
        self.custom_user = input('Enter desired username (5 or less chars) (leave blank if none): ')
        self.successful_joins = 0
        self.failed_joins = 0
        self.lock = threading.Lock()
        self.bots = []

    def joinHandle(self):
        with self.lock:
            self.successful_joins += 1
            print(f"[{self.successful_joins}] Joined!")

    def randName(self, integer):
        return ''.join(random.choice(string.ascii_letters) for _ in range(integer))

    async def _join_game(self, username):
        client = KahootClient()
        client.on("joined", self.joinHandle)
        try:
            await client.join_game(game_pin=self.gamepin, username=username)
            self.bots.append(client)
        except Exception as e:
            with self.lock:
                self.failed_joins += 1
                print(f"Failed: {username} - {e}")

    def joingame(self):
        if self.custom_user == "":
            username = ('xeny ' + '| ' + self.randName(6))
        else:
            username = (self.custom_user + ' | ' + self.randName(6))

        asyncio.run(self._join_game(username))


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

    for x in range(int(Client.botamount)):
        thread = threading.Thread(target=Client.joingame, daemon=True)
        thread.start()
        time.sleep(0.3)

    print("-" * 40)
    print(f"All bots launched! Joined: {Client.successful_joins} | Failed: {Client.failed_joins}")
    print("Bots will stay connected until you close this window.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all bots...")
        print(f"Final count - Joined: {Client.successful_joins} | Failed: {Client.failed_joins}")
