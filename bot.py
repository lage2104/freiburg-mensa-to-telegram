import requests
import yaml
import xml.etree.ElementTree as ET
import telegram
from addict import Dict

# Read YAML file
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)
config = Dict(config)


def build_url(base_url, args_dict):
    args = "&".join("{}={}".format(*i) for i in args_dict.items())
    return f"{base_url}?{args}"


def main():
    bot = telegram.Bot(token=config.telegram_token)
    base_url = "https://www.swfr.de/index.php"
    args = {
        "id": 1400,
        "type": 98,
        "tx_swfrspeiseplan_pi1[apiKey]": config.api_key,
        "tx_swfrspeiseplan_pi1[ort]": config.mensa_id,
        "tx_swfrspeiseplan_pi1[tage]": 1,
    }
    request_url = build_url(base_url, args)
    result = requests.get(request_url)
    tree = ET.ElementTree(ET.fromstring(result.text))
    all_name_elements = tree.findall('.//tagesplan')
    current_day = all_name_elements[0]
    food_today = current_day.findall('.//menue')
    for menue in food_today:
        menue_zusatz = menue.attrib['zusatz'] if 'zusatz' in menue.attrib else ""
        menue_type = menue.attrib['art']
        menue_name = menue.find('.//nameMitUmbruch').text
        menue_allergikerhinweise = menue.find(".//allergikerhinweise").text
        sellerie_warning = True if "sellerie" in menue_allergikerhinweise.lower() else False
        msg = "<b>{}</b>\n<i>{}</i>\n{}".format(menue_type, menue_zusatz, menue_name)
        msg = msg.replace("<br>", "\n")
        bot.send_message(chat_id=config.chat_id, text=msg, parse_mode=telegram.ParseMode.HTML, timeout=10)
        if not sellerie_warning:
            continue
        msg_with_warning = "Achtung 🚨:\n<b>{}</b> kann Sellerie enthalten🥦".format(menue_type)
        bot.send_message(chat_id=config.chat_id, text=msg_with_warning, parse_mode=telegram.ParseMode.HTML, timeout=10)


if __name__ == '__main__':
    main()
