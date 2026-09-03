# KahootTools

A fast, asynchronous Kahoot bot spammer that allows you to join multiple bots to a game with configurable rate limits and custom usernames. Built with Python and asyncio for high performance.

## Features

-  **High-performance joining** – Uses a single `asyncio` event loop to launch hundreds of bots concurrently.
-  **Configurable rate limit** – Set the maximum number of bots joining per second (0 for unlimited).
-  **Custom usernames** – Provide a prefix (up to 5 chars) or leave blank for the default `xeny`.
-  **Random answering** – Each bot automatically picks a random answer for every question.
-  **Simple stop mechanism** – Press `S` (without Enter) to gracefully stop all bots and exit.
-  **Lightweight** – No thread-per-bot overhead; uses async tasks for scalability.

## Requirements

- Python 3.8 or higher
- `kahoot` library (install via `pip install kahoot`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/KahootTools.git
   cd KahootTools
