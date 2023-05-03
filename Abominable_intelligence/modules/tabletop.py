import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from random import randint

from interactions import Extension, SlashContext, slash_command, slash_int_option

class Tabletop(Extension):
    
    @slash_command(description="1d20 by default")
    async def dice(self, ctx: SlashContext, dice:slash_int_option("Dice")=1, sides:slash_int_option("Sides")=20):
        await ctx.channel.trigger_typing()
        await ctx.send(f"{dice}d{sides}: {', '.join([str(randint(1,sides)) for _ in range(dice)])}")

def setup(bot):
    Tabletop(bot)
