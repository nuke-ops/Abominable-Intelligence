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
async def throw(ctx: lightbulb.SlashContext) -> None:
    # Maximum number of fields that can fit in one Discord embed
    max_fields_per_page = 24
    # Total number of pages required to display all dice rolls
    sum_pages = ctx.options.dice // (max_fields_per_page + 1) + 1

    # Roll all dice and calculate the total summary
    dice_rolls, total_summary = roll_all_dice(ctx.options.dice, ctx.options.sides)
    # Build the embeds for displaying results
    embeds = build_embeds(
        dice_rolls,
        total_summary,
        max_fields_per_page,
        sum_pages,
        ctx.options.dice,
        ctx.options.sides,
    )

    # If there's only one embed, respond directly
    if len(embeds) == 1:
        await ctx.respond(embeds[0])
    # Otherwise, send paginated embeds with navigation
    else:
        await send_paginated_embeds(ctx, embeds)


def roll_all_dice(dice: int, sides: int) -> tuple[list[int], int]:
    """
    Rolls all dice and calculates the total summary.

    Args:
        dice: Number of dice to roll.
        sides: Number of sides on each dice.

    Returns:
        A tuple containing a list of dice rolls and the total sum of all rolls.
    """

    rolls = []
    total_summary = 0

    for _ in range(dice):
        throw = randint(1, sides)
        rolls.append(throw)
        total_summary += throw

    return rolls, total_summary


def build_embeds(
    dice_rolls: list[int],
    total_summary: int,
    max_fields_per_page: int,
    sum_pages: int,
    dice: int,
    sides: int,
) -> list[hikari.Embed]:
    """
    Builds the embeds to display the dice rolls.

    Args:
        dice_rolls: List of individual dice roll results.
        total_summary: Sum of all dice rolls.
        max_fields_per_page: Maximum number of fields per embed page.
        sum_pages: Total number of pages.
        dice: Total number of dice rolled.
        sides: Number of sides on each dice.

    Returns:
        A list of Hikari Embed objects, each representing a page.
    """
    embeds = []
    current_page = fields_counter = page_summary = 0

    # Create the first embed
    embed = create_dice_embed()

    # Footer format for each embed page
    page_footer = (
        lambda cur_page, pages, sum_roll_page: f"Page: {cur_page}/{pages} | Page Summary: {sum_roll_page}"
    )

    # Iterate over dice rolls and add them to the embed fields
    for idx, throw in enumerate(dice_rolls, start=1):
        fields_counter += 1
        page_summary += throw

        # Add the roll to the embed
        embed.add_field(
            name=f"{idx}.", value=format_roll_as_ansi(throw, sides), inline=True
        )

        # If the current embed has reached the maximum number of fields, finalize it
        if fields_counter == max_fields_per_page:
            current_page += 1
            embed.set_footer(page_footer(current_page, sum_pages, page_summary))
            embeds.append(embed)

            # Start a new embed for the next page
            embed = create_dice_embed()
            fields_counter = 0
            page_summary = 0

    # Add any remaining dice rolls to the last embed
    if fields_counter > 0:
        current_page += 1
        embed.set_footer(page_footer(current_page, sum_pages, page_summary))
        embeds.append(embed)

    # Add a description to each embed summarizing the rolls
    for embed in embeds:
        embed.description = (
            f"**{dice}** D**{sides}** | Total Summary: **{total_summary}**"
        )

    return embeds


def create_dice_embed() -> hikari.Embed:
    """
    Creates a new base embed with default styling for the dice command.

    Returns:
        A Hikari Embed object.
    """
    embed = hikari.Embed(color=hikari.Color.of(0x00FF00))
    embed.set_author(
        name="Dice",
        icon="https://cdn.discordapp.com/attachments/732923500624347181/1132556441572606012/d20_reversed.png",
    )
    return embed


def format_roll_as_ansi(roll: int, sides: int) -> str:
    """
    Formats a dice roll result using ANSI codes for better visual clarity in Discord.

    Explanation:
        Discord does not allow removing bold effect from text in embed fields.
        So we use ANSI codes to highlight critical rolls:
        - Red for critical success (highest roll) or failure (lowest roll).
        - Orange for all other rolls.

    Args:
        roll: The result of the dice roll.
        sides: Number of sides on the dice (to identify the highest possible roll).

    Returns:
        A string containing the formatted roll with ANSI coloring.
    """
    ansi_color = "[1;31m" if roll == 1 or roll == sides else "[1;33m"
    return f"```ansi\n{ansi_color}{roll}```"


async def send_paginated_embeds(
    ctx: lightbulb.SlashContext, embeds: list[hikari.Embed]
) -> None:
    """
    Sends a paginated response with navigation buttons for multiple embeds.

    Args:
        ctx: The command context.
        embeds: List of embeds to paginate.

    Returns:
        None
    """
    # Define navigation buttons for the paginator
    items: list[nav.NavItem] = [
        nav.FirstButton(label="|<", emoji=None),
        nav.PrevButton(label="<", emoji=None),
        nav.NextButton(label=">", emoji=None),
        nav.LastButton(label=">|", emoji=None),
    ]

    # Create and start the navigator view
    navigator = nav.NavigatorView(pages=embeds, items=items, timeout=118)
    builder = await navigator.build_response_async(ctx.bot.d.miru)
    await builder.create_initial_response(ctx.interaction)
    ctx.app.d.miru.start_view(navigator)


def load(bot):
    bot.add_plugin(plugin)
