import subprocess
import traceback
from interactions import (Extension, OptionType, SlashCommandChoice, SlashContext,
                          slash_command, slash_option, subcommand)

from modules.core import Core
from decorators import administration_only


def list_branches():
    branches = subprocess.check_output('git branch -r'.split()).decode # example output: origin/HEAD -> origin/main \n origin/main \n origin/v1
    # remove head, remove the "origin/"" thingies and transform to list. example: ['main', 'v1']
    return [x.replace("origin/", "").replace("->", "").strip() for x in branches().split("\n") if x and "origin/HEAD" not in x]

class Git(Extension):
    @slash_command(description="Local git management commands")
    async def git(self, ctx: SlashContext):
        pass

    @subcommand("git", description="list local branches")
    @administration_only
    async def branches(self, ctx: SlashContext):
        current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode()
        branches = subprocess.check_output(['git', 'branch', '-r']).decode()
        await ctx.send(f"{branches}\nCurrent branch:{current_branch}")

    @subcommand("git", description="switch active branch")
    @slash_option(name="branch", description="", opt_type=OptionType.STRING, required=True, choices = [SlashCommandChoice(name=branch, value=branch) for branch in list_branches()])
    async def checkout(self, ctx: SlashContext, branch: str):
        branch_set = subprocess.check_output(["git", "checkout", branch]).decode()
        current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode()
        await ctx.send(f"{branch_set}\nCurrent branch: {current_branch}")

    @subcommand("git", description="Update the bot")
    @administration_only
    async def pull(self, ctx: SlashContext): 
        await ctx.send("Looking for changes...")
        try:
            pull = subprocess.check_output(['git', 'pull']).decode("ascii")
            await ctx.send(pull)
            if "Already up to date" not in pull:
                await Core.restart(ctx)
        except Exception:
            await ctx.send("Pull failed")
            traceback.print_exc()

def setup(bot):
    Git(bot)
