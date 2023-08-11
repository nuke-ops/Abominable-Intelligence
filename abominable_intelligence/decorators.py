import functools

from global_variables import role_id_administration


def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        if ctx.member is not None and role_id_administration in [
            role.id for role in ctx.member.get_roles()
        ]:
            await func(ctx, *args, **kwargs)
        else:
            await ctx.respond("You don't have access to that command")

    return wrapper
