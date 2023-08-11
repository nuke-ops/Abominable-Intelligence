import os
import sys
import traceback

import hikari
import lightbulb

from decorators import administration_only

plugin = lightbulb.Plugin("Core")


async def error(ctx: lightbulb.Context, title: str, description: str):
    await ctx.respond(
        embed=hikari.Embed(
            title=title,
            description=f"**Error**: {description}",
            color=hikari.Color.of(0xFF0000),
        )
    )


@plugin.command
@lightbulb.command("restart", "restarts the bot")
@lightbulb.implements(lightbulb.SlashCommand)
@administration_only
async def restart(ctx: lightbulb.Context):
    await ctx.respond("Restarting the bot...")
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