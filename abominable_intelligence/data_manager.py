import os
import json

bot_dir = os.path.dirname(os.path.abspath(__file__))

###
### JSON management
###
# Example usage
# add_element_to_json('config.json', ['person', 'age'], 30)
# remove_element_from_json('config.json', ['person', 'address', 'city'])


def add_element_to_json(file_path: str, keys: list, value: str) -> None:
    file_path = os.path.join(bot_dir + "/data", file_path)
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    current_level = data
    for key in keys[:-1]:
        if key in current_level:
            current_level = current_level[key]
        else:
            current_level[key] = {}
            current_level = current_level[key]
    current_level[keys[-1]] = value
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def remove_element_from_json(file_path: str, keys: list) -> None:
    file_path = os.path.join(bot_dir + "/data", file_path)
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    current_level = data
    for key in keys[:-1]:
        if key in current_level:
            current_level = current_level[key]
        else:
            return
    if keys[-1] in current_level:
        del current_level[keys[-1]]
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


###
### per file functions
###


def config() -> dict:
    try:
        config_file = os.path.join(bot_dir + "/data", "config.json")
        with open(config_file) as conf:
            return json.loads(conf.read())
    except FileNotFoundError:
        print("config file not found")
        return {
            "bot": {},
            "token": os.environ.get("DISCORD_BOT_TOKEN"),
            "owner_id": (),
            "prefix": (),
            "guild_id": (),
        }


def data() -> dict:
    try:
        config_file = os.path.join(bot_dir + "/data", "data.json")
        with open(config_file) as conf:
            return json.loads(conf.read())
    except FileNotFoundError:
        print("data file not found")
        return {
            "core": {"role_id_administration": None},
            "sql": {"encrypt_key": None},
            "ai": {
                "host": "localhost",
                "port": "11434",
                "model": "llama2",
                "temperature": "0.2",
            },
        }
