import logging
import sys
import traceback

import lightbulb
from extensions.core import error

plugin = lightbulb.Plugin("listeners")


@plugin.listener(lightbulb.events.LightbulbStartedEvent)
async def on_ready(event: lightbulb.LightbulbStartedEvent) -> None:
    try:
        print("Bot started, I think")
        logging.info("Abominable intelligence has started!")
        if "restarted" in sys.argv:
            channel_id = sys.argv[sys.argv.index("restarted") + 1]
            sys.argv.remove(sys.argv[sys.argv.index("restarted") + 1])
            sys.argv.remove("restarted")
            await event.bot.rest.create_message(
                channel=channel_id, content="Restart succeeded"
            )
    except Exception:
        traceback.print_exc()


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if not isinstance(event.exception, lightbulb.CommandInvocationError):
        logging.warning(event.exception.original)
        return
    await error(
        ctx=event.context,
        title=event.context.command.name,
        description="Something went wrong during invocation of command",
        error=event.exception.original,
    )
    return


def load(bot):
    bot.add_plugin(plugin)
