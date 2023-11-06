from random import randint

import hikari
import lightbulb
import miru
from extensions.core import error

plugin = lightbulb.Plugin("Tabletop")


@plugin.command
@lightbulb.option("sides", "Amount of sides for each dice", int, default=20)
@lightbulb.option("dice", "Amount of dice", int, default=1)
@lightbulb.command("dice", "rolls the dice")
@lightbulb.implements(lightbulb.SlashCommand)
async def dice(ctx: lightbulb.Context) -> None:
    # some pseudo error handling
    if ctx.options.dice > 500 or ctx.options.sides > 500:
        await error(
            ctx=ctx, title="Dice", description="values can't be bigger than 500"
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

    # figuring this out gave me more headache then it should probably.
    # anyway, I can die in piece now, I don't care if this is the correct way.
    class DicePaginator(miru.View):
        def __init__(self, embeds):
            super().__init__(timeout=300)
            self.embeds = embeds
            self.current_page = 0

        @miru.button(label="|<", style=hikari.ButtonStyle.SUCCESS)
        async def first_page(self, button: miru.Button, ctx: miru.Context):
            self.current_page = 0
            await self.update_page(ctx)

        @miru.button(label="<", style=hikari.ButtonStyle.PRIMARY)
        async def previous_page(self, button: miru.Button, ctx: miru.Context):
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = len(self.embeds) - 1
            await self.update_page(ctx)

        @miru.button(label=">", style=hikari.ButtonStyle.PRIMARY)
        async def next_page(self, button: miru.Button, ctx: miru.Context):
            self.current_page += 1
            if self.current_page >= len(self.embeds):
                self.current_page = 0
            await self.update_page(ctx)

        @miru.button(label=">|", style=hikari.ButtonStyle.SUCCESS)
        async def last_page(self, button: miru.Button, ctx: miru.Context):
            self.current_page = len(self.embeds) - 1
            await self.update_page(ctx)

        async def update_page(self, ctx: miru.Context):
            if self.current_page < sum_pages:
                await ctx.edit_response(embed=self.embeds[self.current_page])
            else:
                await ctx.edit_response(embed=self.embeds[0])

        async def on_timeout(self):
            for button in self.children:
                button.disabled = True
            await self.message.edit(components=self.build())

    if sum_pages <= 1:
        await ctx.respond(embeds[0])
    else:
        paginator_view = DicePaginator(embeds)
        message = await ctx.respond(embed=embeds[0], components=paginator_view.build())
        await paginator_view.start(message)


def load(bot):
    bot.add_plugin(plugin)
