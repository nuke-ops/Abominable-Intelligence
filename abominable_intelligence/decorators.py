import functools
from data_manager import config

config = config()


def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs) -> None:
        admin_role_id = config["role_id_administration"]
        member_roles = [role.id for role in ctx.member.get_roles()]
        member_is_owner = ctx.author.id == config["owner_id"]

        if admin_role_id in member_roles or member_is_owner:
            return await func(ctx, *args, **kwargs)
        await ctx.respond("You don't have access to that command")

    return wrapper
