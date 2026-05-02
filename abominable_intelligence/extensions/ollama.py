import json
import logging
from typing import Any, Generator

import data_manager
import hikari
import lightbulb
import miru
import requests

# from decorators import administration_only
from data_manager import config, data

bot_config = config()["bot"]
ollama_config = data()["ai"]

loader = lightbulb.Loader()
ollama = lightbulb.Group("ai", "Bootleg Ollama module")


def _call(prompt: str) -> Generator[bytes, None, None]:
    address = f"http://{ollama_config['host']}:{ollama_config['port']}/api/generate"
    payload: dict[str, Any] = {
        "model": ollama_config["model"],
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


def _buffered_call(
    prompt: str,
) -> Generator[tuple[str, dict[str, Any]], None, None]:
    buffer = ""
    for part in _call(prompt):
        if part.get("done"):
            yield buffer, part
            break
        buffer += part["response"]
        if len(buffer) >= 32:
            yield buffer, part
            buffer = ""


class OllamaSettingsModal(miru.Modal, title="Ollama Settings"):
    host = miru.TextInput(
        label="host", placeholder="localhost", value=ollama_config["host"]
    )
    port = miru.TextInput(
        label="port", placeholder="11434", value=ollama_config["port"]
    )
    model = miru.TextInput(
        label="model",
        placeholder="llama2",
        value=ollama_config["model"],
    )
    temperature = miru.TextInput(
        label="temperature", placeholder="0.6", value=ollama_config["temperature"]
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


# @administration_only
@ollama.register
class Ollama_settings(
    lightbulb.SlashCommand, name="settings", description="ollama settings"
):
    @lightbulb.invoke
    async def ollama_settings(
        self, ctx: lightbulb.Context, miru_client: miru.Client = lightbulb.di.INJECTED
    ) -> None:
        modal = OllamaSettingsModal()
        builder = modal.build_response(miru_client)
        await builder.create_modal_response(ctx.interaction)
        miru_client.start_modal(modal)


# @lightbulb.option("prompt", "prompt", str, required=True)
# @lightbulb.command("prompt", "Prompt")
# @administration_only
@ollama.register
class Ollama_prompt(lightbulb.SlashCommand, name="prompt", description="prompt"):
    prompt = lightbulb.string("prompt", "prompt for AI")

    @lightbulb.invoke
    async def ollama_prompt(self, ctx: lightbulb.Context) -> None:
        response_content = ""
        x = 0
        template = """Answer the prompt by following these rules:
    1. Keep your responses under 2000 characters.
    2. If you don't know the answer, just say that you don't know, try to not make up an answer.
    3. Use Discord markdown syntax, eg. if it's code block, surround it with triple apostrophes and add the code language on the start eg. "```py"
    The prompt:
    """
        async with ctx.client.app.rest.trigger_typing(ctx.channel_id):
            await ctx.respond(f"> {self.prompt}")
            message = await ctx.interaction.fetch_initial_response()
            for buffer, _ in _buffered_call(template + self.prompt):
                x += 1
                if x > 5:
                    await ctx.client.app.rest.trigger_typing(ctx.channel_id)
                    x = 0
                response_content += buffer
                await message.edit(f"> {self.prompt} \n\n{response_content}")


loader.command(ollama, guilds=[bot_config["guild_id"]])
