import subprocess
import traceback

import lightbulb
from decorators import administration_only
from extensions.core import restart

plugin = lightbulb.Plugin("git")


def _list_branches():
    branches = subprocess.check_output("git branch -r".split()).decode
    # example output of "branches": origin/HEAD -> origin/main \n origin/main \n origin/v1
    # remove head and the "origin/"" thingies, and transform to list.
    # final example output: ['main', 'v1']
    return [
        x.replace("origin/", "").replace("->", "").strip()
        for x in branches().split("\n")
        if x and "origin/HEAD" not in x
    ]


@plugin.command
@lightbulb.command("git", "Local git management commands")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def git(ctx: lightbulb.Context):
    pass


@git.child
@lightbulb.command("branches", "list local branches")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def branches(ctx: lightbulb.Context):
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"]
    ).decode()
    branches = subprocess.check_output(["git", "branch", "-r"]).decode()
    await ctx.respond(f"{branches}\nCurrent branch:{current_branch}")


@git.child
@lightbulb.option("branch", "branch", str, required=True, choices=_list_branches())
@lightbulb.command("checkout", "switch active branch")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def checkout(ctx: lightbulb.Context):
    branch_set = subprocess.check_output(
        ["git", "checkout", ctx.options.branch]
    ).decode()
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"]
    ).decode()
    await ctx.respond(f"{branch_set}\nCurrent branch: {current_branch}")


@git.child
@lightbulb.command("pull", "update the bot")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def pull(ctx: lightbulb.Context):
    await ctx.respond("Looking for changes...")
    try:
        pull = subprocess.check_output(["git", "pull"]).decode("ascii")
        await ctx.respond(pull)
        if "Already up to date" not in pull:
            await restart(ctx)
    except Exception:
        await ctx.respond("Pull failed")
        traceback.print_exc()


def load(bot):
    bot.add_plugin(plugin)
