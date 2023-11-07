import json
import logging

import hikari
import lightbulb
import requests
from extensions.core import error
from extensions.MySQL import Sql

plugin = lightbulb.Plugin("gw2")

sql = Sql().gw2()

api_account = "https://api.guildwars2.com/v2/account"
# someday I'll make it configurable, probably
guild_nukeops = "C632B318-B4AB-EB11-81A8-E944283D67C1"
guild_afk = "5A3B8707-912E-ED11-84B0-06B485C7CFFE"


###
### internal functions
###


def _list_guilds(api_key) -> dict:
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return json.loads(response.text)["guilds"]


def _account_exists(api_key) -> bool:
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return True if response.status_code == 200 else False


###
### commands
###


@plugin.command
@lightbulb.command("gw2", "gw2 commands")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def gw2(ctx: lightbulb.Context) -> None:
    pass


@gw2.child
@lightbulb.command("help", "guide for gw2 commands")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def help(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title="Help",
        description="**Gw2 API documentation**: https://wiki.guildwars2.com/wiki/API:Main\
        \n**Source code of the module**: https://github.com/maksxpl/Abominable-Intelligence/blob/main/abominable_intelligence/extensions/gw2.py",
        color=hikari.Color.of(0xE0FFFF),
    )
    embed.add_field(
        name="/gw2 save-api-key [api_key]",
        value="Saves the api key\
        \nGet the key from https://account.arena.net/applications",
        inline=False,
    )
    embed.add_field(
        name="/gw2 verify",
        value="Assigns ranks based on your in-game guilds\
        \nRequries a stored API key with access to at least the Account API",
        inline=False,
    )
    await ctx.respond(embed=embed)


@gw2.child
@lightbulb.option("api_key", "API key", str, required=True)
@lightbulb.command("save-api-key", "Saves the API key")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def save_api_key(ctx: lightbulb.Context) -> None:
    if not _account_exists(ctx.options.api_key):
        await error(ctx=ctx, title="api_key", description="Invalid API")
        return
    if sql.select(ctx.member.nickname):
        try:
            await ctx.respond("User already in database, overwriting...")
            sql.update(ctx.options.api_key, ctx.member.nickname)
            await ctx.respond("API saved successfully")
            return
        except Exception as e:
            await ctx.respond("Database Error, most likely")
            logging.warning(e)
            return
    try:
        sql.insert(ctx.member.nickname, ctx.options.api_key)
        await ctx.respond("API saved successfully")
    except Exception as e:
        await ctx.respond("Database Error, most likely")
        logging.warning(e)


@gw2.child
@lightbulb.command("verify", "Assigns ranks based on your in-game guilds")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def verify(ctx: lightbulb.Context) -> None:
    api_key = sql.select(ctx.member.nickname)
    if not api_key:
        await ctx.respond("API key not found")
        return
    if not _account_exists(api_key):
        await error(ctx=ctx, title="verify", description="Invalid API")
        return
    output = ""
    player_guilds = _list_guilds(api_key)
    if guild_nukeops in player_guilds:
        await ctx.member.add_role(1012181221704466513)
        output += "Added [NUKE] rank\n"
    if guild_afk in player_guilds:
        await ctx.member.add_role(1017008230444040212)
        output += "Added [AFK] rank\n"
    if output == "":
        await ctx.respond("Guilds not found, none of ranks were asigned")
        return
    await ctx.respond(output)


def load(bot):
    bot.add_plugin(plugin)
