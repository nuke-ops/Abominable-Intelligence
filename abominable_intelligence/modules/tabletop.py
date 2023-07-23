from random import randint

from interactions import Extension, SlashContext, slash_command, slash_int_option, Embed, Color
from interactions.ext.paginators import Paginator

class Tabletop(Extension):
    
    @slash_command(description="1d20 by default")
    async def dice(
        self,
        ctx: SlashContext,
        dice: slash_int_option("Dice") = 1,
        sides: slash_int_option("Sides") = 20,
    ):
        embed = Embed(color="#00FF00")
        embed.set_author(name="Dice", icon_url="https://cdn.discordapp.com/attachments/732923500624347181/1132556441572606012/d20_reversed.png")
        embeds = []
        current_page = fields_counter = summary = page_summary = 0
        max_fields_per_page = 24
        sum_pages = dice//(max_fields_per_page+1)+1

        # throw dice
        for x in range(dice):
            fields_counter += 1
            throw = randint(1, sides)
            summary += throw
            page_summary += throw
            # Discord doesn't allow us to remove bold effect from field name so
            # I decided to make value more visible by coloring it with ansi
            if throw == 1 or throw == sides:
                ansi = "[1;31m"
            else:
                ansi = "[1;33m"
            embed.add_field(name=f"{x + 1}.", value=f"```ansi\n{ansi}{throw}```", inline=True)

            # if filled all embed rows, make a new embed
            if fields_counter == max_fields_per_page:
                current_page += 1
                embeds.append(embed)
                embed.set_footer(f"Page: {current_page}/{sum_pages} | Summary: {page_summary}")
                embed = Embed(color="#00FF00")
                fields_counter = 0
                page_summary = 0

        # if last page wasn't fully filled, add remnant rolls
        if len(embed.fields) < max_fields_per_page:
            current_page += 1
            embed.set_footer(f"Page: {current_page}/{sum_pages} | Summary: {page_summary}")
            embeds.append(embed)

        for x in range(len(embeds)):
            embeds[x].description = f"**{dice}**d**{sides}** | **Summary**: **{summary}**"
        
        await Paginator.create_from_embeds(self.bot, *embeds).send(ctx)

def setup(bot):
    Tabletop(bot)
