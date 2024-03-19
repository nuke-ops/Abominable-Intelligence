import functools

import hikari
import lightbulb
from data_manager import config

config = config()["bot"]


def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx: lightbulb.Context, *args, **kwargs) -> None:
        from extensions.core import is_admin

        if await is_admin(ctx):
            return await func(ctx, *args, **kwargs)
        await ctx.respond(
            "You don't have access to this command", flags=hikari.MessageFlag.EPHEMERAL
        )

    return wrapper
