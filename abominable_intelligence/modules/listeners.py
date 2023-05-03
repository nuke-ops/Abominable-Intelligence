import sys
import traceback
from interactions import Extension, listen
from interactions.api.events import Error

from abominable_intelligence import logger, bot, DEBUG, INFO, WARN, ERROR, SUCCESS
from global_variables import logs_channel

class Listeners(Extension):

    @listen()
    async def on_ready(self):
        try:
            print("Bot started, I think")
            logger.log(INFO, 'Abominable intelligence has started!')
            if len(sys.argv) > 2 and sys.argv[1] == "Restart triggered":
                channel = bot.get_channel(sys.argv[2])
                await channel.send("Restart succeeded")
        except Exception:
            traceback.print_exc()

    @listen()
    async def on_error(self, error: Error):
        await bot.get_channel(logs_channel).send(f"```\n{error.source}\n{error.error}\n```") 

def setup(bot):
    Listeners(bot)
