import time

import multiprocessing
from bots import *

if __name__ == '__main__':
    # Create a multiprocessing process for the bot
    bot_process = multiprocessing.Process(target=mart)

    # Start the bot process
    bot_process.start()

    # Keep the main process running
    while True:
        # Perform any necessary tasks in the main process
        # This can include monitoring the bot process, handling user interactions, etc.
        time.sleep(1)