import logging
import os
import yaml

import hikari
import lightbulb

from global_variables import script_dir, config_path

# set bot's work directory
os.chdir(script_dir)
# load bot token and guild id
try:
    with open(config_path) as conf:
        f = yaml.load(conf, Loader=yaml.FullLoader)
        bot_token = f["bot_token"]
        guild_id = f["guild_id"]
except FileNotFoundError:
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    guild_id = os.environ.get("DISCORD_GUILD_ID)")


bot = lightbulb.BotApp(
    token=bot_token,
    prefix="!test ",
    intents=hikari.Intents.ALL,
    default_enabled_guilds=guild_id,
    logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
        },
    },
)


@bot.command
@lightbulb.option("test", "Amount of times to reapet")
@lightbulb.command("ping", "checks that the bot is alive")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    for x in range(1, int(ctx.options.test) + 1):
        await ctx.respond(f"{x}. Pong")


if __name__ == "__main__":
    bot.load_extensions("extensions.core")
    bot.load_extensions("extensions.tabletop")

    bot.run()
