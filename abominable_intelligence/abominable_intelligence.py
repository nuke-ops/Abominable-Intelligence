import os

import hikari
import lightbulb
import miru
import yaml
from global_variables import config_path, guild_id, script_dir

# set bot's work directory
os.chdir(script_dir)
# load bot token and guild id
try:
    with open(config_path) as conf:
        f = yaml.load(conf, Loader=yaml.FullLoader)
        bot_token = f["bot_token"]
except FileNotFoundError:
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")


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
try:
    miru.install(bot)
except:
    print("Miru is already loaded, apparently, I guess.\nAlso, fuck you miru.")


# to be sure bot is able to write
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

    if os.path.exists(script_dir + "\\extensions\\test.py"):
        bot.load_extensions("extensions.test")

    bot.run()
