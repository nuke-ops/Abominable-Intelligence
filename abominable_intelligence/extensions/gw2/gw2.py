import logging

import lightbulb
from data_manager import config, data
from extensions.core import error, success
from extensions.MySQL import Sql
from hooks import administration_only

from .gw2api import Gw2API

bot_config = config()["bot"]
gw2_data = data()["gw2"]  # renamed to avoid shadowing the `data` import
sql = Sql().Gw2()
guilds = gw2_data["guilds"]

loader = lightbulb.Loader()
gw2_group = lightbulb.Group("gw2", "GW2 commands")


@gw2_group.register
class SaveApiKey(
    lightbulb.SlashCommand,
    name="save-api-key",
    description="Saves the API key",
):
    api_key = lightbulb.string("api_key", "API key")

    @lightbulb.invoke
    async def save_api_key(self, ctx: lightbulb.Context) -> None:
        if not ctx.member:
            return

        api_key = sql.select(ctx.member.username)
        if not Gw2API().account_exists(api_key):
            await error(ctx=ctx, title="api_key", description="Invalid API")
            return
        if sql.select(ctx.member.username):
            try:
                await ctx.respond("User already in database, overwriting...")
                sql.update(self.api_key, ctx.member.username)
                await success(ctx, "save-api-key", "API saved successfully")
                return
            except Exception as e:
                await ctx.respond("Database Error, most likely")
                logging.warning(e)
                return
        try:
            sql.insert(ctx.member.username, self.api_key)
            await ctx.respond("API saved successfully")
        except Exception as e:
            await ctx.respond("Database Error, most likely")
            logging.warning(e)


@gw2_group.register
class Verify(
    lightbulb.SlashCommand,
    name="verify",
    description="Assigns ranks based on your in-game guilds",
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        if not ctx.member:
            return

        api_key = sql.select(ctx.member.username)
        if not api_key:
            await error(ctx=ctx, title="verify", description="API key not found")
            return
        if not Gw2API().account_exists(api_key):
            await error(ctx=ctx, title="verify", description="Invalid API")
            return

        user_guilds = Gw2API().list_guilds(api_key)
        output = ""
        for guild in guilds:
            guild_id = guilds[guild]["id"]
            if guild_id in user_guilds:
                guild_role = guilds[guild]["discord_role"]
                guild_tag = Gw2API().get_guild_tag(guild_id)
                await ctx.member.add_role(guild_role)
                output += f"Added [{guild_tag}] rank\n"
        if output == "":
            await error(
                ctx=ctx,
                title="verify",
                description="Guilds not found, none of ranks were assigned",
            )
            return
        await success(ctx, "verify", output)


@gw2_group.register
class Lookup(
    lightbulb.SlashCommand,
    name="lookup",
    description="Checks game account name of the given discord user",
    hooks=[administration_only],
):
    user = lightbulb.string("user", "Discord account")

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        api_key = sql.select(self.user)
        if not api_key:
            await ctx.respond("User not found")
            return
        await ctx.respond(Gw2API().user_lookup(api_key))


loader.command(gw2_group, guilds=[bot_config["guild_id"]])
