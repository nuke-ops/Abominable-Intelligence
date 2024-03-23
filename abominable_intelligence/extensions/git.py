import subprocess
import traceback

import hikari
import lightbulb
import miru
from extensions.core import error, is_admin, restart, success

plugin = lightbulb.Plugin("git")


def _list_branches() -> list:
    find_branches = (
        subprocess.check_output("git branch -r".split()).decode().split("\n")
    )
    branches = [
        branch.strip().replace("origin/", "")
        for branch in find_branches
        if branch and "HEAD ->" not in branch
    ]
    return branches


async def _pull(ctx) -> None:
    await ctx.respond("Looking for changes...")
    try:
        pull = subprocess.check_output("git pull".split()).decode()
        await ctx.respond(pull)
        if "Already up to date" not in pull:
            await restart(ctx)
    except Exception:
        await ctx.respond("Pull failed")
        traceback.print_exc()


async def _checkout(ctx, branch) -> None:
    try:
        result = subprocess.run(
            f"git checkout {branch}".split(), capture_output=True, text=True, check=True
        )
        branch_set = result.stdout
        current_branch = subprocess.check_output(
            "git branch --show-current".split()
        ).decode()
        await success(ctx, f"Current branch: {current_branch}", branch_set)
    except subprocess.CalledProcessError as e:
        error_output = e.stderr if e.stderr else "No error output available"
        await error(ctx, "checkout", f"Something went wrong: {error_output}", e)
    except Exception as e:
        await error(ctx, "checkout", "An unexpected error occurred", e)


async def _branches(ctx: lightbulb.Context) -> None:
    current_branch = subprocess.check_output(
        "git branch --show-current".split()
    ).decode()
    branches = subprocess.check_output("git branch -r".split()).decode()
    await success(ctx, f"Current branch: {current_branch}", branches)


async def _reset(ctx) -> None:
    message = await ctx.respond("Backing up the branch...")
    try:
        if "local-backup" in _list_branches():
            message = await message.edit(f"Removing old backup")
            remove_backup = subprocess.check_output(
                "git branch --delete local-backup".split()
            ).decode()
            message = await message.edit(f"{remove_backup}")
        backup = subprocess.check_output("git branch local-backup".split()).decode()
        message = await message.edit(f"{backup}\nOld branch backed up")
    except Exception as e:
        await ctx.respond("Backup failed")

    message = await ctx.respond("Resetting the branch...\n")
    try:
        branch_reset = subprocess.check_output("git reset --hard".split()).decode()
        await message.edit(branch_reset)
    except Exception:
        await ctx.respond(message.content + "Reset failed")
        traceback.print_exc()


class GitButtons(miru.View):
    @miru.button(label="Pull", style=hikari.ButtonStyle.PRIMARY)
    async def pull_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await _pull(ctx)

    @miru.button(label="Checkout", style=hikari.ButtonStyle.PRIMARY)
    async def checkout_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not any(isinstance(child, miru.TextSelect) for child in self.children):
            self.add_item(SelectBranch())
            await ctx.message.edit(components=self)

    @miru.button(label="List branches", style=hikari.ButtonStyle.SUCCESS)
    async def branches_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await _branches(ctx)

    @miru.button(label="Hard reset", style=hikari.ButtonStyle.DANGER)
    async def reset_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await _reset(ctx)

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        await self.message.edit(components=self)

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if not await is_admin(ctx):
            await ctx.respond(
                "You don't have access to this command",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False
        return True


class SelectBranch(miru.TextSelect):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Branch",
            options=[miru.SelectOption(label=x) for x in _list_branches()],
        )

    async def callback(self, ctx: miru.ViewContext) -> None:
        print(self.values)
        await _checkout(ctx, self.values[0])

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if not await is_admin(ctx):
            await ctx.respond(
                "You don't have access to this command",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False
        return True


@plugin.command
@lightbulb.command("git", "panel with git commands")
@lightbulb.implements(lightbulb.SlashCommand)
async def git(ctx: lightbulb.SlashContext) -> None:
    view = GitButtons(timeout=120)
    response = await ctx.respond(components=view)
    message = await response
    miru_client: miru.Client = ctx.app.d.miru
    miru_client.start_view(view, bind_to=message)


def load(bot):
    bot.add_plugin(plugin)
