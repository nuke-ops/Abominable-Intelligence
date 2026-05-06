from random import randint
from re import compile as regex_compile

import hikari
import lightbulb
import miru
from miru.ext import nav

loader = lightbulb.Loader()


@loader.command
class Throw(lightbulb.SlashCommand, name="dice", description="rolls the dice"):
    dice_amt = lightbulb.integer(
        "dice", "Amount of dice", default=1, min_value=1, max_value=500
    )
    sides_amt = lightbulb.integer(
        "sides", "Amount of sides for each dice", default=20, min_value=1, max_value=500
    )

    @lightbulb.invoke
    async def throw(
        self, ctx: lightbulb.Context, miru_client: miru.Client = lightbulb.di.INJECTED
    ) -> None:
        # Maximum number of fields that can fit in one Discord embed
        max_fields_per_page = 24
        # Total number of pages required to display all dice rolls
        sum_pages = self.dice_amt // (max_fields_per_page + 1) + 1

        # Roll all dice and calculate the total summary
        dice_rolls, total_summary = roll_all_dice(self.dice_amt, self.sides_amt)
        # Build the embeds for displaying results
        embeds = build_embeds(
            dice_rolls,
            total_summary,
            max_fields_per_page,
            sum_pages,
            self.dice_amt,
            self.sides_amt,
        )

        # If there's only one embed, respond directly
        if len(embeds) == 1:
            await ctx.respond(embeds[0])
        # Otherwise, send paginated embeds with navigation
        else:
            await send_paginated_embeds(ctx, embeds, miru_client)


def roll_all_dice(dice: int, sides: int) -> tuple[list[int], int]:
    """
    Rolls all dice and calculates the total summary.

    Args:
        dice: Number of dice to roll.
        sides: Number of sides on each dice.

    Returns:
        A tuple containing a list of dice rolls and the total sum of all rolls.
    """

    rolls: list[int] = []
    total_summary = 0

    for _ in range(dice):
        throw = randint(1, sides)
        rolls.append(throw)
        total_summary += throw

    return rolls, total_summary


def format_roll_as_ansi(roll: int, sides: int) -> str:
    """
    Formats the dice roll result using ANSI codes for better visual clarity in Discord.

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
    ansi_color = "\x1b[1;31m" if roll == 1 or roll == sides else "\x1b[1;33m"
    return f"```ansi\n{ansi_color}{roll}```"


def create_dice_embed(dice: int, sides: int, total_summary: int) -> hikari.Embed:
    embed = hikari.Embed(
        description=f"**{dice}** D**{sides}** | Total Summary: **{total_summary}**",
        color=hikari.Color.of(0x00FF00),
    )
    embed.set_author(
        name="Dice",
        icon="https://cdn.discordapp.com/attachments/732923500624347181/1132556441572606012/d20_reversed.png",
    )
    return embed


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
    embeds: list[hikari.Embed] = []
    current_page = fields_counter = page_summary = 0

    # Create the first embed
    embed = create_dice_embed(dice, sides, total_summary)

    # Footer format for each embed page
    def page_footer(cur_page: int, pages: int, sum_roll_page: int) -> str:
        return f"Page: {cur_page}/{pages} | Page Summary: {sum_roll_page}"

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
            embed = create_dice_embed(dice, sides, total_summary)  # <-- pass args
            fields_counter = 0
            page_summary = 0

    # Add any remaining dice rolls to the last embed
    if fields_counter > 0:
        current_page += 1
        embed.set_footer(page_footer(current_page, sum_pages, page_summary))
        embeds.append(embed)

    return embeds


async def send_paginated_embeds(
    ctx: lightbulb.Context, embeds: list[hikari.Embed], miru_client: miru.Client
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
    builder = await navigator.build_response_async(miru_client)
    await builder.create_initial_response(ctx.interaction)
    miru_client.start_view(navigator)


###
### Backup text command
###

# Define the regex for "int int"
DICE_REGEX = regex_compile(r"^\d+\s\d+$")


@loader.listener(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent) -> None:
    if event.message.author.is_bot or event.content[:6] != "!dice ":
        return
    message: str = event.content

    dice_command = message[6:].strip()  # Extract the part of the message after "!dice "

    # Check if the message matches the regex
    if not DICE_REGEX.match(dice_command):
        await event.message.respond(
            "Invalid message! Use the format: `!dice <int> <int>`"
        )
    else:
        # If the regex matches, you can safely parse the integers
        dice, sides = map(int, dice_command.split())
        # await roll_dice(dice, sides, event)
        await throw_manual(event, dice, sides)


async def throw_manual(
    ctx: hikari.MessageCreateEvent, dice: int = 1, sides: int = 20
) -> None:
    if dice > 24:
        await ctx.message.respond("Invalid message! Can't roll more than 24 dice")

    # Maximum number of fields that can fit in one Discord embed
    max_fields_per_page = 24
    # Total number of pages required to display all dice rolls
    sum_pages = dice // (max_fields_per_page + 1) + 1

    # Roll all dice and calculate the total summary
    dice_rolls, total_summary = roll_all_dice(dice, sides)
    # Build the embeds for displaying results
    embeds = build_embeds(
        dice_rolls,
        total_summary,
        max_fields_per_page,
        sum_pages,
        dice,
        sides,
    )

    await ctx.message.respond(embeds[0])
