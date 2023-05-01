import functools
import logging
import os
import subprocess
import sys
from random import randint
import traceback

from interactions import (listen, Client, OptionType, SlashCommandChoice,
                          SlashContext, slash_command, slash_int_option,
                          slash_option, subcommand)

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.yaml")

    
# set bot's work directory
os.chdir(script_dir)


# logs for journal
DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# define bot and its settings
bot = Client(
    token=os.environ.get('DISCORD_BOT_TOKEN'),
    default_scope=os.environ.get('DISCORD_GUILD_ID)'),
    # delete_unused_application_cmds=True
)


role_id_administration = 668245500612444205


##
## functions
##

def list_branches():
    branches = subprocess.check_output('git branch -r'.split()).decode # example output: origin/HEAD -> origin/main \n origin/main \n origin/v1
    # remove head, remove the "origin/"" thingies and transform to list. example: ['main', 'v1']
    return [x.replace("origin/", "").replace("->", "").strip() for x in branches().split("\n") if x and "origin/HEAD" not in x]

##
## custom decorators
##

def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx: SlashContext, *args, **kwargs):
        if role_id_administration in [role.id for role in ctx.author.roles]:
            await func(ctx, *args, **kwargs)
        else:
            await ctx.send("You don't have access to that command", hidden=True)
    return wrapper


##
## git commands
##
@slash_command(description="Local git management commands")
async def git(ctx: SlashContext):
    pass

@subcommand("git", description="check remote branches")
@administration_only
async def branches(ctx: SlashContext):
    branches = subprocess.check_output(['git', 'branch', '-r']).decode()
    await ctx.send(branches)

@subcommand("git", description="switch active branch")
@slash_option(name="repo", description="", opt_type=OptionType.STRING, required=True, choices = [SlashCommandChoice(name=branch, value=branch) for branch in list_branches()])
async def checkout(ctx: SlashContext, branch: str):
    if ctx.member.has_role(role_id_administration):
        branch_set = subprocess.check_output(["git", "checkout", branch]).decode()
        branch_current = subprocess.check_output(["git", "branch", "--show-current"]).decode()
        await ctx.send(f"{branch_set}\nCurrent branch: {branch_current}")
    else:
        await ctx.send("You don't have access to that command")

@subcommand("git", description="Update the bot")
@administration_only
async def pull(ctx: SlashContext): 
    await ctx.send("Pulling code from github...")
    try:
        pull = subprocess.check_output(['git', 'pull']).decode("ascii")
        await ctx.send(pull)
        if "Already up to date" not in pull:
            await restart(ctx)
    except Exception:
        await ctx.send("Pull failed")
        traceback.print_exc()

##
## fun commands or something idk
##

@slash_command(description="1d20 by default")
async def dice(ctx: SlashContext, dice:slash_int_option("Dice")=1, sides:slash_int_option("Sides")=20):
    await ctx.channel.trigger_typing()
    await ctx.send(f"{dice}d{sides}: {', '.join([str(randint(1,sides)) for _ in range(dice)])}")


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


bot.start()
