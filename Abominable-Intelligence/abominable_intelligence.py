import logging
import os
import sys
import traceback
import yaml

from interactions import (Client, slash_command, SlashContext)

from abominable_modules import *
from decorators import administration_only
from global_variables import script_dir, config_path

# set bot's work directory
os.chdir(script_dir)

# load bot token and guild id
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
    # delete_unused_application_cmds=True
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
       

if __name__ == '__main__':
    bot.start()
