from random import randint

from interactions import Extension, SlashContext, slash_command, slash_int_option, Embed, Color
from interactions.ext.paginators import Paginator

class Tabletop(Extension):
    
    @slash_command(description="1d20 by default")
    async def dice(self, ctx: SlashContext, dice:slash_int_option("Dice") = 1, sides:slash_int_option("Sides") = 20):
        
        embed = Embed(title = "Dice", color = "#00FF00")
        embeds = []
        rows_counter = 0
        summary = 0
        
        # throw dice
        for x in range(dice):
            rows_counter += 1
            throw = randint(1, sides)
            summary += throw
            embed.add_field(name = str(x+1), value = throw, inline = True)
            
            # if filled all embed rows, make a new embed
            if rows_counter == 24:
                embeds.append(embed)
                embed = Embed(title = "Dice", description = f"{dice}d{sides}", color = "#00FF00")
                rows_counter = 0
                
        # if last page wasn't filled, add remnant rolls
        if len(embed.fields) < 24:
            embeds.append(embed)
            
        embeds[0].description = f"{dice}d{sides} | Sum: {summary}"
        await Paginator.create_from_embeds(self.bot, *embeds).send(ctx)

def setup(bot):
    Tabletop(bot)
