import os
import sys
import traceback

import hikari
import lightbulb
from decorators import administration_only

plugin = lightbulb.Plugin("Core")


async def error(
    ctx: lightbulb.Context,
    title: str = None,
    description: str = None,
    error: str = None,
) -> None:
    await ctx.respond(
        embed=hikari.Embed(
            title=title if title else "Error",
            description=f"{description}\n**Error**: ```{error}```"
            if error
            else description,
            color=hikari.Color.of(0xFF0000),
        )
    )


@plugin.command
@lightbulb.command("restart", "restarts the bot")
@lightbulb.implements(lightbulb.SlashCommand)
@administration_only
async def restart(ctx: lightbulb.Context):
    await ctx.respond("Restarting the bot...")
    await ctx.bot.rest.trigger_typing(ctx.channel_id)
    try:
        # Restart the process, pass last arguments and "restarted" with channel id to catch it in on_ready() in listeners.py module
        os.execv(
            sys.executable,
            ["python"] + sys.argv + ["restarted", str(ctx.channel_id)],
        )
    except Exception:
        await ctx.respond("Restart failed")
        traceback.print_exc()


def load(bot):
    bot.add_plugin(plugin)
