import asyncio
import random
import string
import sys
import threading
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

        while True:
            try:
                self.gamepin = int(input('PIN: '))
                break
            except ValueError:
                print("PIN must be a number.")

        while True:
            try:
                self.botamount = int(input('Amount of bots (max 2000): '))
                break
            except ValueError:
                print("Amount must be a number.")

        self.custom_user = input('Enter desired username (5 or less chars) (leave blank if none): ')

        rate_input = input('Max bots per second (default 10, 0 = unlimited): ').strip()
        try:
            self.max_bots_per_second = float(rate_input) if rate_input else 10.0
        except ValueError:
            print(f"Invalid rate '{rate_input}', defaulting to 10.")
            self.max_bots_per_second = 10.0

        self.successful_joins = 0
        self.failed_joins = 0
        self._failure_counter = 0
        self._consecutive_failures = 0
        self._rate_limit_warned = False
        self._launch_start_time = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._threads = []

    def randName(self, length):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    def _print_progress(self, force=False):
        if not self._launch_start_time:
            return
        with self._lock:
            total = self.successful_joins + self.failed_joins
            success = self.successful_joins
            failed = self.failed_joins
            elapsed = time.time() - self._launch_start_time
        if total % 10 == 0 or force:
            rate = total / elapsed if elapsed > 0 else 0
            print(
                f"\r[{total}/{self.botamount}] Joined: {success} | "
                f"Failed: {failed} | Rate: {rate:.1f}/s   ",
                end='', flush=True,
            )

    def _run_bot_thread(self, username):
        """Run one bot in its own thread + event loop.

        Required because the kahoot library's join_game uses a blocking
        httpx client internally; running bots in parallel threads keeps
        one slow/blocked join from freezing every other bot.
        """
        try:
            asyncio.run(self._bot_coro(username))
        except Exception as e:
            with self._lock:
                self.failed_joins += 1
                self._failure_counter += 1
                n = self._failure_counter
            if n == 1 or n % 25 == 0:
                print(f"\n[Thread error #{n}] {type(e).__name__}: {e}")

    async def _bot_coro(self, username):
        client = KahootClient()

        # Per-bot dedupe: whichever signal arrives first wins.
        state = {"counted": False}
        state_lock = threading.Lock()

        def mark_success():
            with state_lock:
                if state["counted"]:
                    return False
                state["counted"] = True
            with self._lock:
                self.successful_joins += 1
                self._consecutive_failures = 0
            self._print_progress()
            return True

        def mark_failure():
            with state_lock:
                if state["counted"]:
                    return None
                state["counted"] = True
            with self._lock:
                self.failed_joins += 1
                self._failure_counter += 1
                self._consecutive_failures += 1
                n = self._failure_counter
                consecutive = self._consecutive_failures
                warn = False
                if consecutive >= 25 and not self._rate_limit_warned:
                    self._rate_limit_warned = True
                    warn = True
            if warn:
                print(
                    "\n[Notice] Many consecutive join failures detected — "
                    "Kahoot is likely rate-limiting this IP or the game is full."
                )
            return n

        def on_joined(*args, **kwargs):
            # Fires when the WebSocket is confirmed joined. Dedupes
            # against the fallback count below.
            mark_success()

        client.on("joined", on_joined)

        async def answer_random(packet: QuestionStartPacket):
            try:
                num_choices = getattr(packet, 'number_of_choices', 4)
                choice = random.randint(0, num_choices - 1)
                await client.send_answer(choice)
            except Exception:
                pass

        client.on("question_start", answer_random)

        try:
            await client.join_game(self.gamepin, username)
            # Fallback: if the library didn't fire 'joined' but the call
            # returned without error, count it once. Deduped if the
            # callback already fired.
            mark_success()
        except Exception as e:
            n = mark_failure()
            if n is not None and (n == 1 or n % 25 == 0):
                print(f"\n[Join error #{n}] {type(e).__name__}: {e}")
            if hasattr(client, 'disconnect'):
                try:
                    await client.disconnect()
                except Exception:
                    pass
            return

        # Keep alive until stop is requested
        while not self._stop_event.is_set():
            await asyncio.sleep(0.5)

        if hasattr(client, 'disconnect'):
            try:
                await client.disconnect()
            except Exception:
                pass

    def _listen_for_stop(self):
        """Background thread: wait for the user to press 's'."""
        if msvcrt is None:
            # Non-Windows fallback: 's' + Enter
            while not self._stop_event.is_set():
                try:
                    line = sys.stdin.readline()
                    if line.strip().lower() == 's':
                        self._stop_event.set()
                        break
                except Exception:
                    break
            return

        # Flush any keys left over from the input() prompts so a stray
        # Enter or character doesn't immediately trigger a stop.
        try:
            while msvcrt.kbhit():
                msvcrt.getch()
        except Exception:
            pass

        while not self._stop_event.is_set():
            try:
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch.lower() == b's':
                        self._stop_event.set()
                        break
            except Exception:
                pass
            time.sleep(0.05)

    def start_all_bots(self):
        total = self.botamount
        rate_str = self.max_bots_per_second if self.max_bots_per_second > 0 else 'unlimited'
        print(f"\nStarting {total} bots (rate limit: {rate_str} per second)...")
        print("-" * 40)
        print("** Press 's' (no Enter) at any time to stop **\n")

        # Background listener for the stop key
        listener = threading.Thread(target=self._listen_for_stop, daemon=True)
        listener.start()

        interval = 1.0 / self.max_bots_per_second if self.max_bots_per_second > 0 else 0.0
        self._launch_start_time = time.time()

        try:
            for _ in range(total):
                if self._stop_event.is_set():
                    break
                if self.custom_user == "":
                    username = 'xeny' + self.randName(6)
                else:
                    username = self.custom_user + self.randName(6)

                t = threading.Thread(
                    target=self._run_bot_thread,
                    args=(username,),
                    daemon=True,
                )
                t.start()
                self._threads.append(t)

                if interval > 0:
                    time.sleep(interval)

            # Wait until the user presses 's' (or Ctrl+C)
            while not self._stop_event.is_set():
                time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n\nCtrl+C detected. Shutting down...")
            self._stop_event.set()

        self._stop_event.set()
        print("\n\nStop command received. Shutting down...")

        # Give bots a moment to disconnect cleanly
        deadline = time.time() + 3.0
        for t in self._threads:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            t.join(timeout=remaining)

        self._print_progress(force=True)
        print()
        print(
            f"All bots stopped. Final count - "
            f"Joined: {self.successful_joins} | Failed: {self.failed_joins}"
        )
        if self._consecutive_failures >= 25:
            print(
                "Tip: The failure spike at the end usually means Kahoot's "
                "per-IP connection limit kicked in. Try fewer bots, or wait "
                "a minute and retry."
            )


if __name__ == '__main__':
    Client = KahootSpammer()
    print(f"\nGame PIN: {Client.gamepin}")
    print(f"Bots: {Client.botamount}")
    print(
        f"Max bots per second: "
        f"{Client.max_bots_per_second if Client.max_bots_per_second > 0 else 'unlimited'}"
    )
    print(f"Username prefix: {'xeny' if Client.custom_user == '' else Client.custom_user}")
    print("\nConfirm? (y/n): ", end="")
    if input().lower() != 'y':
        print("Cancelled.")
        exit()

    try:
        Client.start_all_bots()
    except KeyboardInterrupt:
        print("\nExiting.")
