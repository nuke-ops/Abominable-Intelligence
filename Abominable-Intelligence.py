import logging
import interactions
import yaml
import datetime
from random import randint


## logs for journal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


with open("config.yaml") as conf:
	f = yaml.load(conf, Loader=yaml.FullLoader)
	bot_token = f["bot_token"]
	guild_id = f["guild_id"]



bot = interactions.Client(
    token=bot_token,
    default_scope=guild_id,
)


@bot.command(
    name="dice",
    description="funny dice",
)
async def _dice(ctx: interactions.CommandContext):
    await ctx.send(randint(1,99))




@bot.event
async def on_ready():
    print("Bot started, I think")
    logger.warning('Abominable inteligence has started!')


bot.start()
