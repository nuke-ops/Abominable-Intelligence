import logging
from random import randint

import interactions
import yaml

## logs for journal
DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
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
    logger.log(INFO, 'Abominable intelligence has started!')


bot.start()
