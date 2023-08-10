import hikari
import lightbulb
from lightbulb.utils import nav
from extensions.core import error

from random import randint

plugin = lightbulb.Plugin("Tabletop")


@plugin.command
@lightbulb.option("sides", "Amount of sides for each dice", int, default=20)
@lightbulb.option("dice", "Amount of dice", int, default=1)
@lightbulb.command("dice", "rolls the dice")
@lightbulb.implements(lightbulb.SlashCommand)
async def dice(ctx: lightbulb.Context):
    # some pseudo error handling
    if ctx.options.dice > 10_000 or ctx.options.sides > 10_000:
        await error(
            ctx=ctx, title="Dice", description="values can't be bigger than 10,000"
        )
        return
    elif ctx.options.dice < 1 or ctx.options.sides < 1:
        await error(ctx=ctx, title="Dice", description="values must be bigger than 0")
        return

    embed = hikari.Embed(color=hikari.Color.of(0x00FF00))
    embed.set_author(
        name="Dice",
        icon="https://cdn.discordapp.com/attachments/732923500624347181/1132556441572606012/d20_reversed.png",
    )

    embeds = []
    current_page = fields_counter = summary = page_summary = 0
    max_fields_per_page = 24
    sum_pages = ctx.options.dice // (max_fields_per_page + 1) + 1

    # throw dice
    for x in range(1, ctx.options.dice + 1):
        fields_counter += 1
        throw = randint(1, ctx.options.sides)
        summary += throw
        page_summary += throw

        # Discord doesn't allow us to remove bold effect from field name so
        # I decided to make value more visible by coloring it with ansi
        if throw == 1 or throw == ctx.options.sides:
            ansi = "[1;31m"  # if roll is critical make it red
        else:
            ansi = "[1;33m"  # otherwise it's orange
        embed.add_field(name=f"{x}.", value=f"```ansi\n{ansi}{throw}```", inline=True)

        # if filled all embed fields, make a new embed
        if fields_counter == max_fields_per_page:
            current_page += 1
            embeds.append(embed)
            embed.set_footer(
                f"Page: {current_page}/{sum_pages} | Summary: {page_summary}"
            )
            embed = hikari.Embed(color=hikari.Color.of(0x00FF00))
            fields_counter = 0
            page_summary = 0

    # if last page wasn't fully filled, add remnant dice rolls
    if len(embed.fields) < max_fields_per_page:
        current_page += 1
        embed.set_footer(f"Page: {current_page}/{sum_pages} | Summary: {page_summary}")
        embeds.append(embed)
    for x in range(len(embeds)):
        description = f"**{ctx.options.dice}**d**{ctx.options.sides}** | **Summary**: **{summary}**"
        embeds[x].description = description

    navigator = nav.ButtonNavigator(embeds)
    await navigator.run(ctx)


def load(bot):
    bot.add_plugin(plugin)
