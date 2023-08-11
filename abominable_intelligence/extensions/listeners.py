import logging
import sys
import traceback

import hikari
import lightbulb
from extensions.core import error
from global_variables import logs_channel

plugin = lightbulb.Plugin("listeners")


@plugin.listener(lightbulb.events.LightbulbStartedEvent)
async def on_ready(event: lightbulb.LightbulbStartedEvent):
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
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await error(
            ctx=event.context,
            title=event.context.command.name,
            description="Something went wrong during invocation of command",
            error=event.exception.original,
        )
    else:
        print("Somethin went wrong")  # I suppose


def load(bot):
    bot.add_plugin(plugin)
