import logging
import os
import subprocess
import sys
from random import randint

import yaml
from interactions import (Client, OptionType, SlashCommandChoice, SlashContext,
                          slash_command, slash_option, subcommand, slash_int_option, slash_default_member_permission, Permissions)

# set os path to bot location for git related commands
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

## logs for journal
DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# load bot token and guild id
with open("config.yaml") as conf:
        f = yaml.load(conf, Loader=yaml.FullLoader)
        bot_token = f["bot_token"]
        guild_id = f["guild_id"]

# define bot and its settings
bot = Client(
    token=bot_token,
    default_scope=guild_id,
    sync_interactions=True,
    delete_unused_application_cmds=True
)

##
## functions
##

def list_branches():
    branches = subprocess.check_output('git branch -r'.split()).decode # example output: origin/HEAD -> origin/main \n origin/main \n origin/v1
    # remove head, remove the "origin/"" thingies and transform to list. example: ['main', 'v1']
    return [x.replace("origin/", "").replace("->", "").strip() for x in branches().split("\n") if x and "origin/HEAD" not in x]

##
## git commands
##
@slash_command(description="GitHub management commands")
async def git(ctx: SlashContext):
    pass

@subcommand("git", description="check remote branches")
async def branches(ctx: SlashContext):
    branches = subprocess.check_output(['git', 'branch', '-r']).decode()
    await ctx.send(branches)

@subcommand("git", description="switch active branch")
@slash_default_member_permission(Permissions.MANAGE_GUILD)
@slash_option(name="repo", description="eh?", opt_type=OptionType.STRING, required=True, choices = [SlashCommandChoice(name=branch, value=branch) for branch in list_branches()])
async def checkout(ctx: SlashContext, branch: str):
    branch_set = subprocess.check_output(["git", "checkout", branch]).decode()
    branch_current = subprocess.check_output(["git", "branch", "--show-current"]).decode()
    await ctx.send(f"{branch_set}\nCurrent branch: {branch_current}")


@subcommand("git", description="Update the bot")
@slash_default_member_permission(Permissions.MANAGE_GUILD)
async def pull(ctx: SlashContext):
        await ctx.send("Pulling code from github...")
        try:
                pull = subprocess.check_output(['git', 'pull']).decode("ascii")
                await ctx.send(pull)

                if "Already up to date" not in pull:
                    await ctx.send("Restarting the bot...")
                    try:
                            os.execv(sys.executable, ['python'] + sys.argv)
                            await ctx.send("Restart succeeded(?)") # todo: pass it as sys.argv and ctx.send it after the restart
                    except Exception:
                            await ctx.send("Restart failed")

        except Exception:
            await ctx.send("Pull failed")

##
## fun commands or something idk
##

# rolls a dice
@slash_command(description="1d20 by default")
async def dice(ctx: SlashContext, dice:slash_int_option("Dice")=1, sides:slash_int_option("Sides")=20):
    await ctx.channel.trigger_typing()
    await ctx.send(f"{dice}d{sides}: {', '.join([str(randint(1,sides)) for _ in range(dice)])}")


@bot.event
async def on_ready():
    print("Bot started, I think")
    logger.log(INFO, 'Abominable intelligence has started!')


bot.start()
