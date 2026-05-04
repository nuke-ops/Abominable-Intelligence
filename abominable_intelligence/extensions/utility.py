import lightbulb
from data_manager import config
from hooks import administration_only

bot_config = config()["bot"]

loader = lightbulb.Loader()


@loader.command
class NameFetch(
    lightbulb.SlashCommand,
    name="fetch_names",
    description="prints all users",
    hooks=[administration_only],
):
    @lightbulb.invoke
    async def name_fetch(self, ctx: lightbulb.Context) -> None:
        members = await ctx.client.rest.fetch_members(ctx.guild_id)

        names: list[str] = [f"<@{x.id}>" for x in members]
        await ctx.respond(" ".join(names))
