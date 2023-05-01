from asyncio import subprocess
import traceback

from interactions import OptionType, SlashCommandChoice, SlashContext, slash_command, slash_option, subcommand
from abominable_intelligence import role_id_administration, restart, administration_only

def list_branches():
    branches = subprocess.check_output('git branch -r'.split()).decode # example output: origin/HEAD -> origin/main \n origin/main \n origin/v1
    # remove head, remove the "origin/"" thingies and transform to list. example: ['main', 'v1']
    return [x.replace("origin/", "").replace("->", "").strip() for x in branches().split("\n") if x and "origin/HEAD" not in x]

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
