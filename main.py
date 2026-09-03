import asyncio
import random
import string
import sys
import time

# Windows-specific keypress detection
try:
    import msvcrt
except ImportError:
    msvcrt = None  # fallback to Enter if not on Windows

from kahoot import KahootClient
from kahoot.packets.server.question_start import QuestionStartPacket


class KahootSpammer:
    def __init__(self):
        print(r'KahootTools - Remastered by Python/er - Originally made by xeny')
        self.gamepin = int(input('PIN: '))
        self.botamount = input('Amount of bots (max 2000): ')
        self.custom_user = input('Enter desired username (5 or less chars) (leave blank if none): ')

        rate_input = input('Max bots per second (default 10, 0 = unlimited): ').strip()
        self.max_bots_per_second = float(rate_input) if rate_input else 10

        self.successful_joins = 0
        self.failed_joins = 0
        self.bots = []                # active clients
        self.tasks = []               # asyncio tasks
        self.semaphore = asyncio.Semaphore(500)  # connection limit
        self._failure_counter = 0     # throttle failure prints

    def randName(self, length):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    async def _close_client_session(self, client):
        """Attempt to close the aiohttp session if it exists."""
        for attr in ('session', '_session', 'client', '_client'):
            session = getattr(client, attr, None)
            if session is not None and hasattr(session, 'close'):
                try:
                    await session.close()
                except Exception:
                    pass

    async def _join_game(self, username):
        client = KahootClient()
        client.on("joined", self._on_joined)

        async def answer_random(packet: QuestionStartPacket):
            num_choices = getattr(packet, 'number_of_choices', 4)
            choice = random.randint(0, num_choices - 1)
            try:
                await client.send_answer(choice)
            except Exception:
                pass

        client.on("question_start", answer_random)

        try:
            async with self.semaphore:
                await client.join_game(game_pin=self.gamepin, username=username)
                self.bots.append(client)
                # Keep alive until cancelled
                while True:
                    await asyncio.sleep(3600)
        except asyncio.CancelledError:
            # Clean disconnect and close session
            if hasattr(client, 'disconnect'):
                try:
                    await client.disconnect()
                except Exception:
                    pass
            await self._close_client_session(client)
            raise
        except Exception as e:
            self.failed_joins += 1
            self._failure_counter += 1
            if self._failure_counter % 10 == 0:
                print(f"\n[Failure] {e}")
        finally:
            # Ensure session is closed even if an unexpected error occurred
            await self._close_client_session(client)

    def _on_joined(self):
        self.successful_joins += 1

    async def _listen_for_stop(self, stop_event):
        """Wait for user to press 's' (no Enter required) and set stop_event."""
        if msvcrt is None:
            # Fallback: require Enter if msvcrt not available (e.g., non-Windows)
            loop = asyncio.get_event_loop()
            while not stop_event.is_set():
                user_input = await loop.run_in_executor(None, sys.stdin.readline)
                if user_input.strip().lower() == 's':
                    stop_event.set()
                    break
            return

        def keypress_listener():
            while not stop_event.is_set():
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch.lower() == b's':
                        stop_event.set()
                        break
                time.sleep(0.05)  # prevent CPU spinning

        # Run the blocking listener in a thread
        await asyncio.to_thread(keypress_listener)

    async def start_all_bots(self):
        total = int(self.botamount)
        print(f"\nStarting {total} bots (rate limit: {self.max_bots_per_second if self.max_bots_per_second > 0 else 'unlimited'} per second)...")
        print("-" * 40)
        print("** Press 's' (no Enter) at any time to stop **")

        # Set a custom exception handler to suppress expected errors during shutdown
        loop = asyncio.get_running_loop()
        def custom_exception_handler(loop, context):
            exception = context.get('exception')
            if isinstance(exception, asyncio.CancelledError):
                # Ignore CancelledError from websocket callbacks
                return
            message = context.get('message', '')
            if 'Event loop is closed' in message or 'closed event loop' in message:
                # Ignore event loop closed errors during shutdown
                return
            # For anything else, print a concise warning (optional)
            print(f"\n[Async Warning] {message}")

        loop.set_exception_handler(custom_exception_handler)

        stop_event = asyncio.Event()
        listener_task = asyncio.create_task(self._listen_for_stop(stop_event))

        interval = 1.0 / self.max_bots_per_second if self.max_bots_per_second > 0 else 0.0

        try:
            for i in range(total):
                if stop_event.is_set():
                    break
                if self.custom_user == "":
                    username = ('xeny' + self.randName(6))
                else:
                    username = (self.custom_user + self.randName(6))
                task = asyncio.create_task(self._join_game(username))
                self.tasks.append(task)
                if interval > 0:
                    await asyncio.sleep(interval)

            # Wait until stop command is given (unless we've already been told to stop)
            if not stop_event.is_set():
                await stop_event.wait()

            print("\nStop command received. Shutting down...")

        finally:
            # Cancel listener and all bot tasks
            listener_task.cancel()
            for task in self.tasks:
                task.cancel()

            # Wait for all bot tasks to finish (with timeout to avoid hanging)
            if self.tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self.tasks, return_exceptions=True),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    print("Timeout waiting for bots to shut down; forcing exit.")

            self.tasks.clear()
            self.bots.clear()
            print(f"All bots stopped. Final count - Joined: {self.successful_joins} | Failed: {self.failed_joins}")


if __name__ == '__main__':
    Client = KahootSpammer()
    print(f"\nGame PIN: {Client.gamepin}")
    print(f"Bots: {Client.botamount}")
    print(f"Max bots per second: {Client.max_bots_per_second if Client.max_bots_per_second > 0 else 'unlimited'}")
    print(f"Username prefix: {'xeny' if Client.custom_user == '' else Client.custom_user}")
    print("\nConfirm? (y/n): ", end="")
    if input().lower() != 'y':
        print("Cancelled.")
        exit()

    # Run the main coroutine; no KeyboardInterrupt handling needed because we use 's' to stop.
    asyncio.run(Client.start_all_bots())
