import logging
import os
import sys
import traceback
import yaml

from interactions import (Client, listen, slash_command, SlashContext)

from abominable_modules import *
from decorators import administration_only


# set bot's work directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# load bot token and guild id
config_path = os.path.join(script_dir, "config.yaml")
with open(config_path) as conf:
    f = yaml.load(conf, Loader=yaml.FullLoader)
    bot_token = f["bot_token"]
    guild_id = f["guild_id"]


# logs for journal
DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# define bot and its settings
bot = Client(
    token=os.environ.get('DISCORD_BOT_TOKEN', bot_token),
    default_scope=os.environ.get('DISCORD_GUILD_ID)', guild_id),
    delete_unused_application_cmds=True
)


@slash_command(description="Restart the bot")
@administration_only
async def restart(ctx = SlashContext):
    await ctx.send("Restarting the bot...")
    try:
        os.execv(sys.executable, ['python'] + sys.argv + ["Restart triggered", str(ctx.channel_id)])
    except Exception:
        await ctx.send("Restart failed")
        traceback.print_exc()

@listen()
async def on_ready():
    try:
        print("Bot started, I think")
        logger.log(INFO, 'Abominable intelligence has started!')
        if len(sys.argv) > 2 and sys.argv[1] == "Restart triggered":
            channel = bot.get_channel(sys.argv[2])
            await channel.send("Restart succeeded")
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    bot.start()
