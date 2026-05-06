import os
import shutil
import sys
import traceback

import hikari
import lightbulb
import miru
from data_manager import add_element_to_json, config, data
from hooks import administration_only

bot_config = config()["bot"]
data = data()
loader = lightbulb.Loader()


async def error(
    ctx: lightbulb.Context,
    title: str,
    description: str,
    exception: Exception | None = None,
) -> None:
    """Send an embed with red border"""
    await ctx.respond(
        embed=hikari.Embed(
            title=title if title else "Error",
            description=(
                f"```{description}```\n**Error**: ```{error}```"
                if exception
                else description
            ),
            color=hikari.Color.of(0xFF0000),
        )
    )


async def success(ctx: lightbulb.Context, title: str, description: str) -> None:
    """Send an embed with green border"""
    await ctx.respond(
        embed=hikari.Embed(
            title=title, description=description, color=hikari.Color.of(0xAAFF00)
        )
    )


async def is_admin(ctx: lightbulb.Context) -> bool:
    admin_role_id: int = data["core"]["role_id_administration"]
    member_roles = [role.id for role in ctx.member.get_roles()]
    member_is_owner = bool(ctx.user.id == bot_config["owner_id"])
    return bool(member_is_owner or admin_role_id in member_roles)


@loader.command(guilds=[bot_config["guild_id"]])
class Restart(
    lightbulb.SlashCommand,
    name="restart",
    description="restarts the bot",
    hooks=[administration_only],
):
    @lightbulb.invoke
    async def restart(self, ctx: lightbulb.Context):
        await ctx.respond("Restarting the bot...")
        await ctx.client.app.rest.trigger_typing(ctx.channel_id)
        # Try to restart the process with the previous arguments and the channel ID for the on_ready() event
        try:
            script = os.path.abspath(__file__)
            main_script = os.path.join(os.path.dirname(script), "..", "main.py")
            main_script = os.path.normpath(main_script)
            uv = shutil.which("uv")
            env = os.environ.copy()
            env["BOT_RESTARTED_CHANNEL"] = str(ctx.channel_id)
            if uv:
                os.execve(uv, ["uv", "run", main_script], env)
            else:
                os.execve(sys.executable, [sys.executable, main_script], env)
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
                add_element_to_json(
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


# @administration_only
@loader.command(guilds=[bot_config["guild_id"]])
class Settings(lightbulb.SlashCommand, name="settings", description="bot settings"):
    @lightbulb.invoke
    async def core_settings(
        self, ctx: lightbulb.Context, miru_client: miru.Client = lightbulb.di.INJECTED
    ) -> None:
        modal = CoreSettingsModal("Bot Settings")
        builder = modal.build_response(miru_client)
        await builder.create_modal_response(ctx.interaction)
        miru_client.start_modal(modal)
