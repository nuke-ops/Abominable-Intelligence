import logging
from random import randint

import os
import subprocess

import interactions
import yaml

os.chdir("/opt/Abominable-Intelligence")

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


@bot.command(
    name="update",
    description="Update the bot",
)
async def _dice(ctx: interactions.CommandContext):
    ctx.send("Pulling code from github...")
    try:
        a = subprocess.check_output(['git', 'pull'])
        await ctx.send(a)
    except Exception as Err:
        await ctx.send("Pull failed")
        await ctx.send(f"Traceback:\n{Err}")
    await ctx.send("Restarting the bot...")
    try:
        await ctx.send("[Placeholder] Restart not implemented yet")
    except:
        await ctx.send("Restart failed")

@bot.event
async def on_ready():
    print("Bot started, I think")
    logger.log(INFO, 'Abominable intelligence has started!')


bot.start()
