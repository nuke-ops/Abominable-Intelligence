import os
import sys
import traceback
from interactions import Embed, Extension, SlashContext, slash_command

from decorators import administration_only


async def error(ctx: SlashContext, title: str, description: str):
    await ctx.send(
        embed=Embed(
            title=title,
            description=f"**Error**: {description}",
            color="#FF0000",
        )
    )


class Core(Extension):
    @slash_command(description="Restart the bot")
    @administration_only
    async def restart(self, ctx: SlashContext):
        await ctx.send("Restarting the bot...")
        try:  # restart the process, pass last arguments and "restarted" with channel id to catch it in on_ready() in listeners.py module
            os.execv(
                sys.executable,
                ["python"] + sys.argv + ["restarted", str(ctx.channel_id)],
            )
        except Exception:
            await ctx.send("Restart failed")
            traceback.print_exc()


def setup(bot):
    Core(bot)
