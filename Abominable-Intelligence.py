import logging
from random import randint

import sys
import traceback
import os
import subprocess

import interactions
import yaml

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

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

def list_branches():
    branches = subprocess.check_output('git branch -r'.split()).decode
    return [x.replace("origin/", "").replace("->", "").strip() for x in branches().split("\n") if x and "origin/HEAD" not in x]

@bot.command(
    name="dice",
    description="roll 1d100",
)
async def dice(ctx: interactions.CommandContext):
    await ctx.send(randint(1,100))


@bot.command(description="GitHub management commands")
async def git(ctx: interactions.CommandContext):
    pass

@git.subcommand(description="check remote branches")
async def branches(ctx: interactions.CommandContext):
    branches = subprocess.check_output(['git', 'branch', '-r']).decode()
    await ctx.send(branches)

@git.subcommand(description="switch active branch")
@interactions.option(required=True, choices = [interactions.Choice(name=branch, value=branch) for branch in list_branches()])
async def checkout(ctx: interactions.CommandContext, branch: str):
    branch_set = subprocess.check_output(["git", "checkout", branch]).decode()
    branch_current = subprocess.check_output(["git", "branch", "--show-current"]).decode()
    await ctx.send(f"{branch_set}\nCurrent branch: {branch_current}")


@bot.command(
    name="update",
    description="Update the bot",
)
async def _update(ctx: interactions.CommandContext):
        await ctx.send("Pulling code from github...")
        try:
                pull = subprocess.check_output(['git', 'pull']).decode("ascii")
                await ctx.send(pull)

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
