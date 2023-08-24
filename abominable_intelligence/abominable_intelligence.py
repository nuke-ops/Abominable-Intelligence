import os

import hikari
import lightbulb
import miru
from data_manager import bot_dir, config

# set bot's work directory
os.chdir(bot_dir)

config = config()
if not config["bot_token"]:
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")

bot = lightbulb.BotApp(
    token=config["bot_token"],
    prefix=config["prefix"],
    intents=hikari.Intents.ALL,
    owner_ids=config["owner_id"],
    default_enabled_guilds=config["guild_id"],
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

try:
    miru.install(bot)
except:
    print("Miru is already loaded, apparently, I guess.\nAlso, fuck you miru.")


# to ensure the bot's ability to write
@bot.listen(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent):
    if event.content and bot.get_me().mention in event.content:
        await event.message.respond("You mentioned me!")


if __name__ == "__main__":
    bot.load_extensions("extensions.core")
    bot.load_extensions("extensions.listeners")

    bot.load_extensions("extensions.git")
    bot.load_extensions("extensions.tabletop")
    bot.load_extensions("extensions.gw2")

    if os.path.exists(bot_dir + "/extensions/test.py"):
        bot.load_extensions("extensions.test")

    bot.run()
