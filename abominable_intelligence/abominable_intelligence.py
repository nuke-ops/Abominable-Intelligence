import logging
import os
import yaml

import hikari
import lightbulb
import miru

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
    guild_id = int(os.environ.get("DISCORD_GUILD_ID"))


bot = lightbulb.BotApp(
    token=bot_token,
    prefix="!aa ",
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
miru.install(bot)

if __name__ == "__main__":
    bot.load_extensions("extensions.core")

    bot.load_extensions("extensions.git")
    bot.load_extensions("extensions.tabletop")
    bot.load_extensions("extensions.gw2")

    bot.run()
