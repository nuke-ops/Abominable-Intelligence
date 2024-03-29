import os

import hikari
import lightbulb
import miru
from data_manager import bot_dir, config

os.chdir(bot_dir)  # set bot's work directory

config = config()["bot"]
bot = lightbulb.BotApp(
    token=config["token"],
    prefix=config["prefix"],
    intents=hikari.Intents.ALL,
    owner_ids=config["owner_id"],
    default_enabled_guilds=config["guild_id"],
    logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            # "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
        },
    },
)

bot.d.miru = miru.Client(bot)

if __name__ == "__main__":
    bot.load_extensions("extensions.core")
    bot.load_extensions("extensions.listeners")

    bot.load_extensions("extensions.git")
    bot.load_extensions("extensions.tabletop")
    bot.load_extensions("extensions.gw2")

    bot.load_extensions("extensions.ollama")

    if os.path.exists(bot_dir + "/extensions/test.py"):
        bot.load_extensions("extensions.test")

    bot.run()
