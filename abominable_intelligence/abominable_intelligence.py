import logging
import os
import yaml

from interactions import Client

from global_variables import script_dir, config_path

# logs for journal
DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# define bot and its settings
bot = Client(
    token=(bot_token),
    default_scope=(guild_id),
    # delete_unused_application_cmds=True
)


if __name__ == "__main__":
    bot.load_extension("modules.listeners")
    bot.load_extension("modules.core")

    bot.load_extension("modules.git")
    bot.load_extension("modules.tabletop")
    bot.load_extension("modules.gw2")

    bot.start()
