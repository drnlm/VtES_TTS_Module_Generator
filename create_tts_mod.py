#!/usr/bin/env python3

import copy
import datetime
import json
import string
import sys
import urllib.request

DATAFILE_URL = 'https://static.krcg.org/data/vtes.json'

OUTPUT_FILE = 'VtES_TTS_Module.json'

# We just take these values from the original TTS file
BASE_DATA = """{"TabStates":
{"0": {"title": "Rules", "body": "", "color": "Grey", "visibleColor": {"r": 0.5, "g": 0.5, "b": 0.5}, "id": 0},
"1": {"title": "White", "body": "", "color": "White", "visibleColor": {"r": 1.0, "g": 1.0, "b": 1.0}, "id": 1},
"2": {"title": "Brown", "body": "", "color": "Brown", "visibleColor": {"r": 0.443, "g": 0.231, "b": 0.09}, "id": 2},
"3": {"title": "Red", "body": "", "color": "Red", "visibleColor": {"r": 0.856, "g": 0.1, "b": 0.094}, "id": 3},
"4": {"title": "Orange", "body": "", "color": "Orange", "visibleColor": {"r": 0.956, "g": 0.392, "b": 0.113}, "id": 4},
"5": {"title": "Yellow", "body": "", "color": "Yellow", "visibleColor": {"r": 0.905, "g": 0.898, "b": 0.172}, "id": 5},
"6": {"title": "Green", "body": "", "color": "Green", "visibleColor": {"r": 0.192, "g": 0.701, "b": 0.168}, "id": 6},
"7": {"title": "Blue", "body": "", "color": "Blue", "visibleColor": {"r": 0.118, "g": 0.53, "b": 1.0}, "id": 7},
"8": {"title": "Teal", "body": "", "color": "Teal", "visibleColor": {"r": 0.129, "g": 0.694, "b": 0.607}, "id": 8},
"9": {"title": "Purple", "body": "", "color": "Purple", "visibleColor": {"r": 0.627, "g": 0.125, "b": 0.941}, "id": 9},
"10": {"title": "Pink", "body": "", "color": "Pink", "visibleColor": {"r": 0.96, "g": 0.439, "b": 0.807}, "id": 10},
"11": {"title": "Black", "body": "", "color": "Black", "visibleColor": {"r": 0.25, "g": 0.25, "b": 0.25}, "id": 11}},
"Grid": {"Type": 0, "Lines": false, "Color": {"r": 0.0, "g": 0.0, "b": 0.0}, "Opacity": 0.75, "ThickLines": false, "Snapping": false, "Offset": false, "BothSnapping": false, "xSize": 2.0, "ySize": 2.0, "PosOffset": {"x": 0.0, "y": 1.0, "z": 0.0}},
"Lighting": {"LightIntensity": 0.54, "LightColor": {"r": 1.0, "g": 0.9804, "b": 0.8902}, "AmbientIntensity": 1.3, "AmbientType": 0, "AmbientSkyColor": {"r": 0.5, "g": 0.5, "b": 0.5}, "AmbientEquatorColor": {"r": 0.5, "g": 0.5, "b": 0.5}, "AmbientGroundColor": {"r": 0.5, "g": 0.5, "b": 0.5}, "ReflectionIntensity": 1.0, "LutIndex": 0, "LutContribution": 1.0},
"Hands": {"Enable": true, "DisableUnused": false, "Hiding": 0},
"ComponentTags": {"labels": []},
"Turns": {"Enable": false, "Type": 0, "TurnOrder": [], "Reverse": false, "SkipEmpty": false, "DisableInteractions": false, "PassTurns": true, "TurnColor": ""},
"DecalPallet": [],
"LuaScript": "--[[ Lua code. See documentation: https://api.tabletopsimulator.com/ --]]\\n\\n--[[ The onLoad event is called after the game save finishes loading. --]]\\nfunction onLoad()\\n    --[[ print(\'onLoad!\') --]]\\nend\\n\\n--[[ The onUpdate event is called once per frame. --]]\\nfunction onUpdate()\\n    --[[ print(\'onUpdate loop!\') --]]\\nend", "LuaScriptState": "", "XmlUI": "<!-- Xml UI. See documentation: https://api.tabletopsimulator.com/ui/introUI/ -->",
"ObjectStates": []}
"""

CRYPT_BACK = "https://static.krcg.org/card/cardbackcrypt.jpg"
LIB_BACK = "https://static.krcg.org/card/cardbacklibrary.jpg"

OTHER_BAG = 'Other'


# TTS will assign GUIDS, so we can leave that unassigned
CARD_TEMPLATE = {
    "GUID": "",
    "Name": "CardCustom",
    "Transform": {
        "posX": -6.0617013,
        "posY": 3.16591716,
        "posZ": 1.09125674,
        "rotX": -1.05527088E-05,
        "rotY": 179.997238,
        "rotZ": 180.0,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "scaleZ": 1.0
    },
    "Nickname": None,
    "Description": "",
    "GMNotes": "",
    "ColorDiffuse": {
        "r": 0.713235259,
        "g": 0.713235259,
        "b": 0.713235259
    },
    "Locked": False,
    "Grid": True,
    "Snap": True,
    "IgnoreFoW": False,
    "Autoraise": True,
    "Sticky": True,
    "Tooltip": True,
    "GridProjection": False,
    "HideWhenFaceDown": True,
    "Hands": True,
    "CardID": None,
    "SidewaysCard": False,
    "CustomDeck": {
    },
    "XmlUI": "",
    "LuaScript": "",
    "LuaScriptState": "",
}


BAG_TEMPLATE = {
    "GUID": "",
    "Name": "Bag",
    "Transform": {
        "posX": 0,
        "posY": 0,
        "posZ": -14,
        "rotX": 0,
        "rotY": 0,
        "rotZ": 0,
        "scaleX": 1.13392854,
        "scaleY": 1.0,
        "scaleZ": 1.11125,
    },
    "Nickname" : None,
    "Description": "",
    "GMNotes": "",
    "ColorDiffuse": {},
    "LayoutGroupSortIndex": 0,
    "Value": 0,
    "Locked": True,
    "Grid": True,
    "Snap": True,
    "IgnoreFoW": False,
    "MeasureMovement": False,
    "DragSelectable": True,
    "Autoraise": True,
    "Sticky": True,
    "Tooltip": True,
    "GridProjection": False,
    "HideWhenFaceDown": False,
    "Hands": False,
    "MaterialIndex": -1,
    "MeshIndex": -1,
    "Bag": {
        "Order": 0,
    },
    "ContainedObjects": [],
    "XmlUI": "",
    "LuaScript": "",
    "LuaScriptState": "",
}


LIB_COLOR = {
    "r": 0.1289998,
    "g": 0.694,
    "b": 0.606999934,
}

CRYPT_COLOR = {
    "r": 0.7058823,
    "g": 0.366520882,
    "b": 0,
}

BAG_START_X = -23.5
BAG_START_Y = 0.775
BAG_START_Z = 14.2

BAG_SMALL_X_OFFSET = 3
BAG_LARGE_X_OFFSET = 9
BAG_MAX_X = 25
BAG_Z_OFFSET = 5.5


def is_crypt(krcg_json_card: dict) -> bool:
    """Identify if a card is a crypt card"""
    if 'Imbued' in krcg_json_card['types'] or 'Vampire' in krcg_json_card['types']:
        return True
    return False


def fetch_json() -> dict:
    link = urllib.request.urlopen(DATAFILE_URL)
    data = link.read()
    cards = json.loads(data)
    return cards


def load_local_file(filename: str) -> dict:
    with open(filename) as f:
        cards = json.load(f)
    return cards


def create_tts_json_card(krcg_json_card: dict) -> dict:
    tts_card = copy.deepcopy(CARD_TEMPLATE)
    tts_card['Nickname'] = krcg_json_card['name']
    tts_card['CardID'] = f"{krcg_json_card['id']}00"
    dCustomDeck = {
         "FaceURL": krcg_json_card['url'],
         "NumWidth": 1,
         "NumHeight": 1,
         "BackIsHidden": True,
         "UniqueBack": False,
         "Type": 1,
    }
    if is_crypt(krcg_json_card):
        dCustomDeck['BackURL'] = CRYPT_BACK
    else:
        dCustomDeck['BackURL'] = LIB_BACK
    tts_card['CustomDeck'][krcg_json_card['id']] = dCustomDeck
    return tts_card


def create_tts_bag(krcg_json_cards: list[dict], bag_name: str,
                   crypt: bool, x: float, y: float, z: float) -> dict:
    if bag_name != OTHER_BAG:
        selection = lambda x: x.lower().startswith(bag_name.lower())
    else:
        selection = lambda x: x.lower()[0] not in string.ascii_lowercase
    bag = copy.deepcopy(BAG_TEMPLATE)
    if crypt:
        bag['Nickname'] = f'Cards: {bag_name} (Crypt)'
        bag['ColorDiffuse'] = CRYPT_COLOR
    else:
        bag['Nickname'] = f'Cards: {bag_name} (Library)'
        bag['ColorDiffuse'] = LIB_COLOR
    for card in krcg_json_cards:
        if selection(card['name']):
            if is_crypt(card) == crypt:
                tts_card = create_tts_json_card(card)
                bag['ContainedObjects'].append(tts_card)
    bag['Transform']['posX'] = x
    bag['Transform']['posY'] = y
    bag['Transform']['posZ'] = z
    return bag


def write_tts_module(tts_bags: list[dict]) -> None:
    cur_time = datetime.datetime.now()
    data = {
        'SaveName': "Updated Vampire: The Eternal struggle cards (full) Vtes - " + cur_time.strftime("%Y-%m-%d"),
        "EpochTime": int(cur_time.timestamp()),
        "Date": cur_time.strftime("%d/%m/%Y %r"),
        "VersionNumber": "v14",
        "GameMode": "VTES2025",
        "GameType": "",
        "GameComplexity": "",
        "Tags": [],
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "Table": "Table_Custom",
        "TableURL": "http://cloud-3.steamusercontent.com/ugc/2291837013385809859/43237B7BA6517D91EA6159D008CD99FD278A30EA/",
        "Sky": "Sky_Downtown",
    }
    data.update(json.loads(BASE_DATA))
    for bag in tts_bags:
        data['ObjectStates'].append(bag)

    with open(OUTPUT_FILE, 'w') as f:
        # We want to preserve unicode in the input
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        card_data = load_local_file(sys.argv[1])
    else:
        card_data = fetch_json()
    tts_bags = []
    x = BAG_START_X
    y = BAG_START_Y
    z = BAG_START_Z
    for bag in string.ascii_uppercase:
        tts_bags.append(create_tts_bag(card_data, bag, True, x, y, z))
        x += BAG_SMALL_X_OFFSET
        tts_bags.append(create_tts_bag(card_data, bag, False, x, y, z))
        x += BAG_LARGE_X_OFFSET
        if x > BAG_MAX_X:
            x = BAG_START_X
            z -= BAG_Z_OFFSET
    tts_bags.append(create_tts_bag(card_data, OTHER_BAG, True, x, y, z))
    x += BAG_SMALL_X_OFFSET
    tts_bags.append(create_tts_bag(card_data, OTHER_BAG, False, x, y, z))
    write_tts_module(tts_bags)
