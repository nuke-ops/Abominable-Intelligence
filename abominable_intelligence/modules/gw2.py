import requests
import json
from interactions import (
    Extension,
    SlashContext,
    Embed,
    slash_command,
    slash_str_option,
    subcommand,
)
from modules.MySQL import Sql


class Gw2api:
    def __init__(self):
        self.account = "https://api.guildwars2.com/v2/account"

    def guilds(self, api_key):
        print(api_key)
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(self.account, headers=headers)
        return json.loads(response.text)["guilds"]

    def account_exists(self, api_key):
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(self.account, headers=headers)
        return True if response.status_code == 200 else False


class Gw2(Extension):
    def __init__(self, ctx):
        self.gw2api = Gw2api()

        self.guild_nukeops = "C632B318-B4AB-EB11-81A8-E944283D67C1"
        self.guild_afk = "5A3B8707-912E-ED11-84B0-06B485C7CFFE"

        self.sql = Sql().gw2()

    @slash_command(description="Guild Wars 2 commands")
    async def gw2(self, ctx: SlashContext):
        pass

    @subcommand("gw2", description="Get help for gw2 commands")
    async def help(self, ctx: SlashContext):
        embed = Embed(description="Help", color="#E0FFFF")
        embed.add_field(
            name="Save API key",
            value="get the key from https://account.arena.net/applications",
            inline=False,
        )
        embed.add_field(
            name="Verify",
            value="Requries stored API key with access to Account API",
            inline=False,
        )
        await ctx.send(embed=embed)

    @subcommand(
        "gw2", name="save-api-key", description="Saves your API in the bot's database"
    )
    async def save_api_key(
        self, ctx: SlashContext, api_key: slash_str_option("API Key")
    ):
        if not self.gw2api.account_exists(api_key):
            await ctx.send("Invalid API")
            return
        if self.sql.select(ctx.author.nickname):
            try:
                await ctx.send("User already in database, overwriting...")
                self.sql.update(api_key, ctx.author.nickname)
                await ctx.send("API saved successfully")
                return
            except Exception as e:
                await ctx.send("Database Error, most likely")
                return
        try:
            self.sql.insert(ctx.author.nickname, api_key)
            await ctx.send("API saved successfully")
        except:
            await ctx.send("Database Error, most likely")

    @subcommand("gw2", description="Asigns you ranks based on your guilds")
    async def verify(self, ctx: SlashContext):
        api_key = str(self.sql.select(ctx.author.nickname))
        if api_key:
            output = ""
            if self.guild_nukeops in self.gw2api.guilds(api_key):
                await ctx.author.add_role(1012181221704466513)
                output += "Added [NUKE] rank\n"
            if self.guild_afk in self.gw2api.guilds(api_key):
                await ctx.author.add_role(1017008230444040212)
                output += "Added [AFK] rank\n"
            if output != "":
                await ctx.send(output)
            else:
                await ctx.send("Guilds not found, none of ranks were asigned")
        else:
            await ctx.send("API key not found")


def setup(bot):
    Gw2(bot)