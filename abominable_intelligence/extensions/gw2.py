import json
import logging

import lightbulb
import requests
from data_manager import config, data
from extensions.core import error, success
from extensions.MySQL import Sql

bot_config = config()["bot"]
data = data()["gw2"]
sql = Sql().gw2()

plugin = lightbulb.Plugin("gw2", default_enabled_guilds=[bot_config["guild_id"]])

api_account = "https://api.guildwars2.com/v2/account/"
api_guild = "https://api.guildwars2.com/v2/guild/"

guilds = data["guilds"]


def _list_guilds(api_key) -> list:
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return json.loads(response.text)["guilds"]


def _get_guild_tag(guild_id) -> str:
    response = requests.get(api_guild + guild_id)
    return json.loads(response.text)["tag"]


def _account_exists(api_key) -> bool:
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return True if response.status_code == 200 else False


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
    if not _account_exists(ctx.options.api_key):
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
    if not _account_exists(api_key):
        await error(ctx=ctx, title="verify", description="Invalid API")
        return

    user_guilds = _list_guilds(api_key)
    output = ""
    for guild in guilds:
        guild_id = guilds[guild]["id"]
        if guild_id in user_guilds:
            guild_role = guilds[guild]["discord_role"]
            guild_tag = _get_guild_tag(guild_id)
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


def load(bot):
    bot.add_plugin(plugin)
