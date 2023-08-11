import json

import hikari
import lightbulb
import requests
from extensions.core import error
from extensions.MySQL import Sql

plugin = lightbulb.Plugin("gw2")


api_account = "https://api.guildwars2.com/v2/account"
# someday I'll make it configurable, probably
guild_nukeops = "C632B318-B4AB-EB11-81A8-E944283D67C1"
guild_afk = "5A3B8707-912E-ED11-84B0-06B485C7CFFE"

sql = Sql().gw2()

###
### internal functions
###


def _list_guilds(api_key):
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return json.loads(response.text)["guilds"]


def _account_exists(api_key):
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_account, headers=headers)
    return True if response.status_code == 200 else False


###
### commands
###


@plugin.command
@lightbulb.command("gw2", "gw2 commands")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def gw2(ctx: lightbulb.Context):
    pass


@gw2.child
@lightbulb.command("help", "guide for gw2 commands")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def help(ctx: lightbulb.Context):
    embed = hikari.Embed(description="Help", color=hikari.Color.of(0xE0FFFF))
    embed.add_field(
        name="Save API key",
        value="get the key from https://account.arena.net/applications",
        inline=False,
    )
    embed.add_field(
        name="Verify",
        value="Requries stored API key with access to at least the Account API",
        inline=False,
    )
    await ctx.respond(embed=embed)


@gw2.child
@lightbulb.option("api_key", "API key", str, required=True)
@lightbulb.command("save-api-key", "Saves the API key in the bot's database")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def save_api_key(ctx: lightbulb.Context):
    if not _account_exists(ctx.options.api_key):
        await error(ctx, "api_key", "Invalid API")
        return
    if sql.select(ctx.member.nickname):
        try:
            await ctx.respond("User already in database, overwriting...")
            sql.update(ctx.options.api_key, ctx.member.nickname)
            await ctx.respond("API saved successfully")
            return
        except Exception as e:
            await ctx.respond("Database Error, most likely")
            return
    try:
        sql.insert(ctx.member.nickname, ctx.options.api_key)
        await ctx.respond("API saved successfully")
    except:
        await ctx.respond("Database Error, most likely")


@gw2.child
@lightbulb.command("verify", "Asigns ranks based on your in-game guilds")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def verify(ctx: lightbulb.Context):
    api_key = sql.select(ctx.member.nickname).decode("utf-8")
    if api_key:
        output = ""
        if guild_nukeops in _list_guilds(api_key):
            await ctx.member.add_role(1012181221704466513)
            output += "Added [NUKE] rank\n"
        if guild_afk in _list_guilds(api_key):
            await ctx.member.add_role(1017008230444040212)
            output += "Added [AFK] rank\n"
        if output != "":
            await ctx.respond(output)
        else:
            await ctx.respond("Guilds not found, none of ranks were asigned")
    else:
        await ctx.respond("API key not found")


def load(bot):
    bot.add_plugin(plugin)
