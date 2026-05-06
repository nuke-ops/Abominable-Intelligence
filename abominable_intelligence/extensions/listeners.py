import logging
import os
import sys
import traceback

import hikari
import lightbulb
from extensions.core import error

loader = lightbulb.Loader()


@loader.listener(hikari.StartingEvent)
async def on_ready(event: hikari.StartingEvent) -> None:
    try:
        print("Bot started, I think")
        logging.info("Abominable intelligence has started!")

        channel_id = os.environ.get("BOT_RESTARTED_CHANNEL")
        if channel_id:
            del os.environ["BOT_RESTARTED_CHANNEL"]
            await event.app.rest.create_message(
                channel=int(channel_id), content="Restart succeeded"
            )

    except Exception:
        traceback.print_exc()


@loader.error_handler
async def on_error(exc: lightbulb.exceptions.ExecutionPipelineFailedException) -> bool:
    ctx = exc.context
    await error(
        ctx=ctx,
        title=ctx.command._command_data.name,
        description="Something went wrong during invocation of command",
        exception=exc.__cause__,
    )
    return True  # True = error was handled, False = not handled
