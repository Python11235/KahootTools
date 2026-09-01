import string
import random
import time
import threading
import asyncio
from kahoot import KahootClient
from kahoot.packets.server.question_start import QuestionStartPacket


class KahootSpammer:
    def __init__(self):
        print(r'KahootTools - Remastered by Python/er - Originally made by xeny')
        self.gamepin = int(input('PIN: '))
        self.botamount = input('Amount of bots (max 2000): ')
        self.custom_user = input('Enter desired username (5 or less chars) (leave blank if none): ')
        self.successful_joins = 0
        self.failed_joins = 0
        self.lock = threading.Lock()
        self.bots = []
        self.running = True  # Flag to control bot operation
        self.stop_event = threading.Event()  # Event for signaling stop

    def joinHandle(self):
        with self.lock:
            self.successful_joins += 1
            print(f"[{self.successful_joins}] Joined!")

    def randName(self, integer):
        return ''.join(random.choice(string.ascii_letters) for _ in range(integer))

    async def _join_game(self, username):
        client = KahootClient()
        client.on("joined", self.joinHandle)

        # Handler to submit a random answer for each question
        async def answer_random(packet: QuestionStartPacket):
            if self.stop_event.is_set():
                return  # Stop answering if stop flag is set
            
            # Determine the number of choices; using getattr for safety as the exact attribute may vary.
            num_choices = getattr(packet, 'number_of_choices', 4)
            # Pick a random answer index (0 to num_choices-1)
            choice = random.randint(0, num_choices - 1)
            try:
                # Using 'send_answer' as it is the logical method name.
                # The exact name may be different (e.g., 'send_response').
                await client.send_answer(choice)
            except Exception as e:
                # Silently fail to keep the bot running if answer submission fails
                pass

        client.on("question_start", answer_random)

        try:
            await client.join_game(game_pin=self.gamepin, username=username)
            self.bots.append(client)
            
            # Keep the bot running until stop event is set
            while not self.stop_event.is_set():
                await asyncio.sleep(0.1)
                
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

    def stop_bots(self):
        """Stop all bots and disconnect them"""
        print("\nStopping all bots...")
        self.stop_event.set()
        self.running = False
        
        # Close all client connections
        for bot in self.bots:
            try:
                # Try to disconnect the bot
                if hasattr(bot, 'disconnect'):
                    asyncio.run(bot.disconnect())
                elif hasattr(bot, 'close'):
                    asyncio.run(bot.close())
            except Exception as e:
                # Silently handle disconnection errors
                pass
        
        self.bots.clear()
        print(f"All bots stopped. Final count - Joined: {self.successful_joins} | Failed: {self.failed_joins}")

    def reserve_stop(self):
        """Reserve the stop function for later use"""
        print("\nStop function has been reserved.")
        print("You can call Client.stop_bots() to stop all bots.")
        print("Note: The stop function will disconnect all bots and clear the bot list.")

    def stop_bots_async(self):
        """Asynchronous version of stop_bots"""
        asyncio.run(self._stop_bots_async())
    
    async def _stop_bots_async(self):
        """Async implementation of stopping bots"""
        print("\nStopping all bots asynchronously...")
        self.stop_event.set()
        self.running = False
        
        # Close all client connections asynchronously
        for bot in self.bots:
            try:
                if hasattr(bot, 'disconnect'):
                    await bot.disconnect()
                elif hasattr(bot, 'close'):
                    await bot.close()
            except Exception as e:
                # Silently handle disconnection errors
                pass
        
        self.bots.clear()
        print(f"All bots stopped. Final count - Joined: {self.successful_joins} | Failed: {self.failed_joins}")


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
        if not Client.running:  # Check if stop was triggered
            break
        thread = threading.Thread(target=Client.joingame, daemon=True)
        thread.start()
        time.sleep(0.3)

    print("-" * 40)
    print(f"All bots launched! Joined: {Client.successful_joins} | Failed: {Client.failed_joins}")
    print("Bots will stay connected and answer questions randomly.")
    print("Press Ctrl+C to stop.")
    
    # Reserve the stop function
    Client.reserve_stop()

    try:
        while Client.running:
            time.sleep(1)
    except KeyboardInterrupt:
        # Use the reserved stop function
        Client.stop_bots()
