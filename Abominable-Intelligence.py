import logging
from random import randint

import sys
import traceback
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

#todo? merge both branch functions into one
@bot.command(
    name="git-branch-check",
    description="check remote branches",
)
async def _branch_check(ctx: interactions.CommandContext):
        a = subprocess.check_output(['git', 'branch', '-r'])
        await ctx.send(a.decode())
        
@bot.command(
    name="git-branch-set",
    description="sets active branch",
)
async def _branch_check(ctx: interactions.CommandContext, branch: str):
        a = subprocess.check_output(['git', 'checkout', branch])
        await ctx.send(a.decode())

@bot.command(
    name="update",
    description="Update the bot",
)
async def _update(ctx: interactions.CommandContext):
        await ctx.send("Pulling code from github...")
        try:
                a = subprocess.check_output(['git', 'pull'])
                await ctx.send(a.decode("ascii"))

                # if updated successfully, restart the bot
                await ctx.send("Restarting the bot...")
                try:
                        os.execv(sys.executable, ['python'] + sys.argv)
                        await ctx.send("Restart succeeded(?)") # todo: move it to argument
                except Exception:
                        await ctx.send(f"Traceback:\n{traceback.format_exc()}")
                        await ctx.send("Restart failed")

        except Exception:
            await ctx.send("Pull failed")
            await ctx.send(f"Traceback:\n{traceback.format_exc()}")


@bot.event
async def on_ready():
    print("Bot started, I think")
    logger.log(INFO, 'Abominable intelligence has started!')


bot.start()
