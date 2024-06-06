import os

import hikari
import lightbulb
import miru
from data_manager import bot_dir, config

os.chdir(bot_dir)  # set bot's work directory

bot_config = config()["bot"]

bot = lightbulb.BotApp(
    token=bot_config["token"],
    prefix=bot_config["prefix"],
    intents=hikari.Intents.ALL,
    owner_ids=bot_config["owner_id"],
    default_enabled_guilds=[bot_config["guild_id"]],
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

print(bot.default_enabled_guilds)

bot.d.miru = miru.Client(bot)

if __name__ == "__main__":
    # core modules
    bot.load_extensions("extensions.core")
    bot.load_extensions("extensions.listeners")

    # global modules
    bot.load_extensions("extensions.tabletop")
    bot.load_extensions("extensions.ollama")

    # guild modules
    bot.load_extensions("extensions.git")
    bot.load_extensions("extensions.gw2.gw2")

    # external modules
    if os.path.exists(bot_dir + "/extensions/test.py"):
        bot.load_extensions("extensions.test")

    bot.run()
