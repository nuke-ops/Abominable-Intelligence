import os
import sys
import traceback
from interactions import Extension, SlashContext, slash_command

from decorators import administration_only

class Core(Extension):
    
    @slash_command(description="Restart the bot")
    @administration_only
    async def restart(self, ctx: SlashContext):
        await ctx.send("Restarting the bot...")
        try:
            os.execv(sys.executable, ['python'] + sys.argv + ["restarted", str(ctx.channel_id)])
        except Exception:
            await ctx.send("Restart failed")
            traceback.print_exc()

def setup(bot):
    Core(bot)
