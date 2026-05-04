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
    mode = lightbulb.string(
        "mode",
        "method of name fetch",
        choices=[
            lightbulb.Choice("id", "id"),
            lightbulb.Choice("username", "username"),
            lightbulb.Choice("cache", "cache"),
        ],
    )

    @lightbulb.invoke
    async def name_fetch(self, ctx: lightbulb.Context) -> None:
        print(self.mode)
        if self.mode == "id":  # ping with no mention
            members = await ctx.client.rest.fetch_members(ctx.guild_id)
            names: list[str] = [f"<@{x.id}>" for x in members]
        elif self.mode == "username":  # list of usernames with no ping
            members = await ctx.client.rest.fetch_members(ctx.guild_id)
            names: list[str] = [f"@{x.username}" for x in members]
        elif self.mode == "cache":  # raw list of IDs
            members = ctx.client.app.cache.get_members_view_for_guild(ctx.guild_id)
            names: list[str] = [f"#{x}!" for x in members]

        await ctx.respond(" ".join(names))
