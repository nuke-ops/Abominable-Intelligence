import json
import logging
from typing import Generator

import data_manager
import hikari
import lightbulb
import miru
import requests
from decorators import administration_only
from extensions.core import error
from data_manager import config, data

bot_config = config()["bot"]
ollama_settings = data()["ai"]
plugin = lightbulb.Plugin("ollama", default_enabled_guilds=[])


def _call(prompt) -> Generator[bytes, None, None]:
    address = f"http://{ollama_settings['host']}:{ollama_settings['port']}/api/generate"
    payload = {
        "model": ollama_settings["model"],
        "prompt": prompt,
        "options": {
            "temperature": 0.6,
        },
    }
    try:
        r = requests.post(address, json=payload)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return

    for line in r.iter_lines(decode_unicode=True):
        if line.strip():
            yield json.loads(line)


def _buffered_call(prompt) -> Generator[tuple[str, dict], None, None]:
    buffer = ""
    for part in _call(prompt):
        if part.get("done"):
            yield buffer, part
            break
        buffer += part["response"]
        if len(buffer) >= 32:
            yield buffer, part
            buffer = ""


class OllamaSettingsModal(miru.Modal):
    host = miru.TextInput(
        label="host", placeholder="localhost", value=ollama_settings["host"]
    )
    port = miru.TextInput(
        label="port", placeholder="11434", value=ollama_settings["port"]
    )
    model = miru.TextInput(
        label="model",
        placeholder="llama2",
        value=ollama_settings["model"],
    )
    temperature = miru.TextInput(
        label="temperature", placeholder="0.6", value=ollama_settings["temperature"]
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        if (
            self.host.value
            and self.port.value
            and self.model.value
            and self.temperature.value
        ):
            try:
                data_manager.add_element_to_json(
                    "data.json", ["ai", "host"], self.host.value
                )
                data_manager.add_element_to_json(
                    "data.json", ["ai", "port"], self.port.value
                )
                data_manager.add_element_to_json(
                    "data.json", ["ai", "model"], self.model.value
                )
                data_manager.add_element_to_json(
                    "data.json", ["ai", "temperature"], self.temperature.value
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
@lightbulb.command("ai", "Bootleg Ollama module")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def ai(ctx: lightbulb.Context) -> None:
    pass


@ai.child
@lightbulb.command("settings", "ollama settings", guilds=[bot_config["guild_id"]])
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def ollamaSettings(ctx: lightbulb.SlashContext) -> None:
    modal = OllamaSettingsModal("Ollama Settings")
    builder = modal.build_response(ctx.bot.d.miru)
    await builder.create_modal_response(ctx.interaction)
    ctx.bot.d.miru.start_modal(modal)


@ai.child
@lightbulb.option("prompt", "prompt", str, required=True)
@lightbulb.command("prompt", "Prompt")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def ai_prompt(ctx: lightbulb.Context) -> None:
    response_content = ""
    x = 0
    template = """Answer the prompt by following these rules:
1. Keep your responses under 2000 characters.
2. If you don't know the answer, just say that you don't know, try to not make up an answer.
3. Use Discord markdown syntax, eg. if it's code block, surround it with triple apostrophes and add the code language on the start eg. "```py"
The prompt:
"""
    async with ctx.bot.rest.trigger_typing(ctx.channel_id):
        message = await ctx.respond(f"> {ctx.options.prompt}")
        for buffer, part in _buffered_call(template + ctx.options.prompt):
            x += 1
            if x > 5:
                await ctx.bot.rest.trigger_typing(ctx.channel_id)
                x = 0
            response_content += buffer
            await message.edit(f"> {ctx.options.prompt} \n\n{response_content}")


def load(bot):
    bot.add_plugin(plugin)
