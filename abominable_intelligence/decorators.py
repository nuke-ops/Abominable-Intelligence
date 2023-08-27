import functools
from data_manager import config

config = config()


def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        if ctx.member is not None:
            if (
                config["role_id_administration"]
                in [role.id for role in ctx.member.get_roles()]
                or ctx.author.id == config["owner_id"]
            ):
                await func(ctx, *args, **kwargs)
            else:
                await ctx.respond("You don't have access to that command")

    return wrapper
