import sys
import traceback
from interactions import Extension, listen
from interactions.api.events import Error

from abominable_intelligence import logger, DEBUG, INFO, WARN, ERROR, SUCCESS
from global_variables import logs_channel


class Listeners(Extension):
    @listen()
    async def on_ready(self):
        try:
            print("Bot started, I think")
            logger.log(INFO, "Abominable intelligence has started!")
            if "restarted" in sys.argv:
                channel = self.bot.get_channel(
                    sys.argv[sys.argv.index("restarted") + 1]
                )
                sys.argv.remove(sys.argv[sys.argv.index("restarted") + 1])
                sys.argv.remove("restarted")
                await channel.send("Restart succeeded")
        except Exception:
            traceback.print_exc()

    @listen()
    async def on_error(self, error: Error):
        await self.bot.get_channel(logs_channel).send(
            f"```\n{error.source}\n{error.error}\n```"
        )


def setup(bot):
    Listeners(bot)
