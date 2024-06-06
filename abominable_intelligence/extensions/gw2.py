from datetime import timedelta
import json
import logging

import lightbulb
import requests
from data_manager import config, data
from extensions.core import administration_only, error, success
from extensions.MySQL import Sql

bot_config = config()["bot"]
data = data()["gw2"]
sql = Sql().gw2()

plugin = lightbulb.Plugin("gw2", default_enabled_guilds=[bot_config["guild_id"]])


guilds = data["guilds"]


class Gw2API:
    def __init__(self, api_key):
        self.headers = {"Authorization": "Bearer " + api_key}
        self.api_account = "https://api.guildwars2.com/v2/account/"
        self.api_guild = "https://api.guildwars2.com/v2/guild/"
        self.api_worlds = "https://api.guildwars2.com/v2/worlds"

    def _convert_age(self, age_seconds: int) -> str:
        return f"{age_seconds}s / {round(age_seconds/3600, 2)}h"

    def _created(self, date: str) -> str:
        return date.replace("T", " ").replace("Z", "")

    def _convert_world(self, world_id: int) -> str:
        world_data = requests.get(f"{self.api_worlds}?ids={world_id}").json()[0]
        region = (
            "EU"
            if str(world_id)[0] == "2"
            else ("NA" if str(world_id)[0] == "1" else None)
        )
        return f"{world_data.get('name', 'unknown')} ({region})"

    def _convert_value(self, key, value):
        if key == "age":
            return self._convert_age(value)
        elif key == "created":
            return self._created(value)
        elif key == "world":
            return self._convert_world(value)
        else:
            return value

    def list_guilds(self, api_key) -> list:
        response = requests.get(self.api_account, headers=self.headers)
        return json.loads(response.text)["guilds"]

    def get_guild_tag(self, guild_id) -> str:
        response = requests.get(self.api_guild + guild_id)
        return json.loads(response.text)["tag"]

    def account_exists(self, api_key) -> bool:
        response = requests.get(self.api_account, headers=self.headers)
        return True if response.status_code == 200 else False

    def user_lookup(self) -> str:
        account_info_json = requests.get(self.api_account, headers=self.headers).json()

        exclude = ["guilds", "guild_leader", "commander", "daily_ap", "monthly_ap"]
        account_info = "\n".join(
            [
                f"[2;31m{key}[0m: {self._convert_value(key, value)}"
                for key, value in account_info_json.items()
                if key not in exclude
            ]
        )
        return f"```ansi\n{account_info}```"


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
    if not Gw2API(api_key).account_exists():
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
    api_key = sql.select(ctx.member.user)
    if not api_key:
        await error(ctx=ctx, title="verify", description="API key not found")
        return
    if not Gw2API(api_key).account_exists():
        await error(ctx=ctx, title="verify", description="Invalid API")
        return

    user_guilds = Gw2API(api_key).list_guilds()
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
@gw2.child
@lightbulb.option(
    "user",
    "discord account",
    str,
    required=True,
    choices=sql.select_all(),  # remove if there will be more than 25 users (won't happen)
)
@lightbulb.command("lookup", "checks game account name of the given discord user")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def lookup(ctx: lightbulb.SlashContext) -> None:
    api_key = sql.select(ctx.options.user)
    await ctx.respond(Gw2API(api_key).user_lookup())


def load(bot):
    bot.add_plugin(plugin)
