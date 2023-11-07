import json
import logging

import data_manager
import lightbulb
import requests
from decorators import administration_only
from extensions.core import error

plugin = lightbulb.Plugin("ollama")


def call(prompt) -> dict:
    config = data_manager.data()["ai"]
    address = f"http://{config['host']}:{config['port']}/api/generate"
    data = {
        "model": "codellama:13b-instruct-q4_1",
        "prompt": prompt,
        "options": {
            "temperature": 0.6,
        },
    }
    try:
        r = requests.post(address, json=data)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return

    for line in r.iter_lines(decode_unicode=True):
        if line.strip():
            yield json.loads(line)


def buffered_call(prompt) -> dict:
    buffer = ""
    for part in call(prompt):
        if part.get("done"):
            yield buffer, part
            break
        buffer += part["response"]
        if len(buffer) >= 32:
            yield buffer, part
            buffer = ""


@plugin.command
@lightbulb.command("ai", "Bootleg Ollama module")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def ai(ctx: lightbulb.Context) -> None:
    pass


@ai.child
@lightbulb.command("set", "settings")
@lightbulb.implements(lightbulb.SlashSubGroup)
async def set(ctx: lightbulb.Context) -> None:
    pass


@set.child
@lightbulb.option("address", "localhost by default", str, required=True)
@lightbulb.command("host", "adress of the ollama api")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def ai_host(ctx: lightbulb.Context) -> None:
    try:
        data_manager.add_element_to_json(
            "data.json", ["ai", "host"], ctx.options.address
        )
        await ctx.respond(f"address ``{ctx.options.address}`` saved")
    except:
        await error(ctx, "ai set host", "Something went wrong")


@set.child
@lightbulb.option("port", "11434 by default", int, required=True)
@lightbulb.command("port", "port of the ollama api")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def ai_port(ctx: lightbulb.Context) -> None:
    try:
        data_manager.add_element_to_json("data.json", ["ai", "port"], ctx.options.port)
        await ctx.respond(f"port ``{ctx.options.port}`` saved")
    except:
        await error(ctx, "ai set port", "Something went wrong")


@ai.child
@lightbulb.option("prompt", "prompt", str, required=True)
@lightbulb.command("prompt", "Prompt")
@lightbulb.implements(lightbulb.SlashSubCommand)
@administration_only
async def ai_prompt(ctx: lightbulb.Context) -> None:
    response_content = ""
    message = await ctx.respond(f"> {ctx.options.prompt}")
    await ctx.bot.rest.trigger_typing(ctx.channel_id)
    x = 0
    template = """Answer the question at the end by following these rules:
1. Keep your responses under 2000 characters.
2. If you don't know the answer, just say that you don't know, try to not make up an answer.
3. surround everything outside code blocks with double apostrophes (``)
Question:
"""
    for buffer, part in buffered_call(template + ctx.options.prompt):
        x += 1
        if x > 5:
            await ctx.bot.rest.trigger_typing(ctx.channel_id)
            x = 0
        response_content += buffer
        await message.edit(f"> {ctx.options.prompt} \n\n{response_content}")


def load(bot):
    bot.add_plugin(plugin)
