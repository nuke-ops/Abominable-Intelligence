from interactions import SlashContext, slash_command, slash_int_option


@slash_command(description="1d20 by default")
async def dice(ctx: SlashContext, dice:slash_int_option("Dice")=1, sides:slash_int_option("Sides")=20):
    await ctx.channel.trigger_typing()
    await ctx.send(f"{dice}d{sides}: {', '.join([str(randint(1,sides)) for _ in range(dice)])}")
