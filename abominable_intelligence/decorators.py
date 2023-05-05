import functools

from global_variables import role_id_administration

def administration_only(func):
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        if role_id_administration in [role.id for role in ctx.author.roles]:
            await func(self, ctx, *args, **kwargs)
        else:
            await ctx.respond("You don't have access to that command", ephemeral=True)
    return wrapper
