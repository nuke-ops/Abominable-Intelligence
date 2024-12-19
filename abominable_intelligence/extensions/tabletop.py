from random import randint

import hikari
import lightbulb
from miru.ext import nav

plugin = lightbulb.Plugin("Tabletop", default_enabled_guilds=[])


@plugin.command
@lightbulb.option(
    "sides",
    "Amount of sides for each dice",
    int,
    default=20,
    min_value=1,
    max_value=500,
)
@lightbulb.option("dice", "Amount of dice", int, default=1, min_value=1, max_value=500)
@lightbulb.command("dice", "rolls the dice")
@lightbulb.implements(lightbulb.SlashCommand)
async def dice(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(color=hikari.Color.of(0x00FF00))
    embed.set_author(
        name="Dice",
        icon="https://cdn.discordapp.com/attachments/732923500624347181/1132556441572606012/d20_reversed.png",
    )  # TODO figure out how to use local images ~~eventually host them on the server~~

    embeds = []
    current_page = fields_counter = summary = page_summary = 0
    max_fields_per_page = 24
    sum_pages = ctx.options.dice // (max_fields_per_page + 1) + 1

    page_footer = (
        lambda cur_page, sum_pages, sum_roll_page: f"Page: {cur_page}/{sum_pages} | Page Summary: {sum_roll_page}"
    )

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
            embed.set_footer(page_footer(current_page, sum_pages, page_summary))
            embed = hikari.Embed(color=hikari.Color.of(0x00FF00))
            fields_counter = 0
            page_summary = 0

    # if last page wasn't fully filled, add remnant dice rolls
    if len(embed.fields) < max_fields_per_page:
        current_page += 1
        embed.set_footer(page_footer(current_page, sum_pages, page_summary))
        embeds.append(embed)
    for x in range(len(embeds)):
        description = f"**{ctx.options.dice}** D**{ctx.options.sides}** | Total Summary: **{summary}**"
        embeds[x].description = description
    # send embed if it's just a one page
    if sum_pages <= 1:
        await ctx.respond(embeds[0])
    # send navigator if there's more pages
    else:
        items: list[nav.NavItem] = [
            nav.FirstButton(label="|<", emoji=None),
            nav.PrevButton(label="<", emoji=None),
            nav.NextButton(label=">", emoji=None),
            nav.LastButton(label=">|", emoji=None),
        ]

        navigator = nav.NavigatorView(pages=embeds, items=items, timeout=120)
        builder = await navigator.build_response_async(ctx.bot.d.miru)
        await builder.create_initial_response(ctx.interaction)
        ctx.app.d.miru.start_view(navigator)


def load(bot):
    bot.add_plugin(plugin)
