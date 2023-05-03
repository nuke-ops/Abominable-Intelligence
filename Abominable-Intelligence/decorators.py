import functools
from interactions import SlashContext

from global_variables import role_id_administration

def administration_only(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: SlashContext, *args, **kwargs):
        if role_id_administration in [role.id for role in ctx.author.roles]:
            await func(self, ctx, *args, **kwargs)
        else:
            await ctx.send("You don't have access to that command", hidden=True)
    return wrapper
