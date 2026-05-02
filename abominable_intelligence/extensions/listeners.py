import logging
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
        if "restarted" in sys.argv:
            channel_id = int(sys.argv[sys.argv.index("restarted") + 1])
            sys.argv.remove(sys.argv[sys.argv.index("restarted") + 1])
            sys.argv.remove("restarted")
            await event.app.rest.create_message(
                channel=channel_id, content="Restart succeeded"
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
        error=exc.__cause__,
    )
    return True  # True = error was handled, False = not handled
