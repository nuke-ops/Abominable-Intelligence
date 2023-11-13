import os
import sys
import traceback

import hikari
import lightbulb
import miru
import data_manager
from decorators import administration_only

plugin = lightbulb.Plugin("Core")
config = data_manager.config()
data = data_manager.data()


async def error(
    ctx: lightbulb.Context,
    title: str = None,
    description: str = None,
    error: str = None,
) -> None:
    await ctx.respond(
        embed=hikari.Embed(
            title=title if title else "Error",
            description=f"```{description}```\n**Error**: ```{error}```"
            if error
            else description,
            color=hikari.Color.of(0xFF0000),
        )
    )


async def success(ctx: lightbulb.Context, title: str, description: str) -> None:
    await ctx.respond(
        embed=hikari.Embed(
            title=title, description=description, color=hikari.Color.of(0xAAFF00)
        )
    )


async def is_admin(ctx: lightbulb.Context):
    admin_role_id = data["core"]["role_id_administration"]
    member_roles = [role.id for role in ctx.member.get_roles()]
    member_is_owner = bool(ctx.author.id == config["owner_id"])
    return bool(member_is_owner or admin_role_id in member_roles)


@plugin.command
@lightbulb.command("restart", "restarts the bot")
@lightbulb.implements(lightbulb.SlashCommand)
@administration_only
async def restart(ctx: lightbulb.Context):
    await ctx.respond("Restarting the bot...")
    await ctx.bot.rest.trigger_typing(ctx.channel_id)
    try:
        # Restart the process with the previous arguments plus a channel ID for the on_ready() function from listeners.py module
        os.execv(
            sys.executable,
            ["python"] + sys.argv + ["restarted", str(ctx.channel_id)],
        )
    except Exception:
        await ctx.respond("Restart failed")
        traceback.print_exc()


class CoreSettingsModal(miru.Modal):
    settings = data["core"]
    role_id_administration = miru.TextInput(
        label="administration rank", value=settings["role_id_administration"]
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        if self.role_id_administration.value:
            try:
                data_manager.add_element_to_json(
                    "data.json",
                    ["core", "role_id_administration"],
                    self.role_id_administration.value,
                )
                await ctx.respond("Settings saved!", flags=hikari.MessageFlag.EPHEMERAL)
                return
            except:
                await ctx.respond(
                    "Something went wrong", flags=hikari.MessageFlag.EPHEMERAL
                )
                return
        await ctx.respond(
            "All fields must be filled", flags=hikari.MessageFlag.EPHEMERAL
        )


@plugin.command
@lightbulb.command("settings", "Bot settings")
@lightbulb.implements(lightbulb.SlashCommand)
@administration_only
async def coreSettings(ctx: lightbulb.SlashContext) -> None:
    modal = CoreSettingsModal("Bot Settings")
    await modal.send(ctx.interaction)
    await modal.wait()


def load(bot):
    bot.add_plugin(plugin)
