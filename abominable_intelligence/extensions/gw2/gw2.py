import logging

import lightbulb
from data_manager import config, data
from extensions.core import administration_only, error, success
from extensions.MySQL import Sql

from .gw2api import Gw2API

bot_config = config()["bot"]
data = data()["gw2"]
sql = Sql().Gw2()
guilds = data["guilds"]

plugin = lightbulb.Plugin("gw2", default_enabled_guilds=[bot_config["guild_id"]])


@plugin.command
@lightbulb.command("gw2", "gw2 commands")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def gw2(ctx: lightbulb.Context) -> None:
    pass


@gw2.child
@lightbulb.option("api_key", "API key", str, required=True)
@lightbulb.command("save-api-key", "Saves the API key", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def save_api_key(ctx: lightbulb.SlashContext) -> None:
    api_key = sql.select(ctx.options.user)
    if not Gw2API.account_exists(api_key):
        await error(ctx=ctx, title="api_key", description="Invalid API")
        return
    if sql.select(ctx.member.username):
        try:
            await ctx.respond("User already in database, overwriting...")
            sql.update(ctx.options.api_key, ctx.member.username)
            await success(ctx, "save-api-key", "API saved successfully")
            return
        except Exception as e:
            await ctx.respond("Database Error, most likely")
            logging.warning(e)
            return
    try:
        sql.insert(ctx.member.username, ctx.options.api_key)
        await ctx.respond("API saved successfully")
    except Exception as e:
        await ctx.respond("Database Error, most likely")
        logging.warning(e)


@gw2.child
@lightbulb.command(
    "verify", "Assigns ranks based on your in-game guilds", ephemeral=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def verify(ctx: lightbulb.SlashContext) -> None:
    api_key = sql.select(ctx.member.username)
    if not api_key:
        await error(ctx=ctx, title="verify", description="API key not found")
        return
    if not Gw2API.account_exists(api_key):
        await error(ctx=ctx, title="verify", description="Invalid API")
        return

    user_guilds = Gw2API.list_guilds(api_key)
    output = ""
    for guild in guilds:
        guild_id = guilds[guild]["id"]
        if guild_id in user_guilds:
            guild_role = guilds[guild]["discord_role"]
            guild_tag = Gw2API.get_guild_tag(guild_id)
            await ctx.member.add_role(guild_role)
            output += f"Added [{guild_tag}] rank\n"
    if output == "":
        await error(
            ctx=ctx,
            title="verify",
            description="Guilds not found, none of ranks were asigned",
        )
        return
    await success(ctx, "verify", output)


@administration_only
@gw2.child()
@lightbulb.option(
    "user",
    "discord account",
    str,
    required=True,
)
@lightbulb.command("lookup", "checks game account name of the given discord user")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def lookup(ctx: lightbulb.SlashContext) -> None:
    api_key = sql.select(ctx.options.user)
    await ctx.respond(Gw2API.user_lookup(api_key))


def load(bot):
    bot.add_plugin(plugin)
