import hikari
import lightbulb


@lightbulb.hook(lightbulb.ExecutionSteps.CHECKS)
async def administration_only(pl: lightbulb.ExecutionPipeline, ctx: lightbulb.Context):
    from extensions.core import is_admin

    if not await is_admin(ctx):
        await ctx.respond(
            "You don't have access to this command.", flags=hikari.MessageFlag.EPHEMERAL
        )
        raise RuntimeError("user has no permissions to access this command")
