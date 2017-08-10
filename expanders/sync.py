import argparse, json, io
from plistlib import readPlist, writePlist

import uuid
from datetime import datetime

ak_default_trigger_char = ";"



def get_te(abbreviation=None, plain_text=None):
    return {
        'abbreviation': abbreviation,
        'abbreviationMode': 0,
        'creationDate': datetime.now(),
        'label': '',
        'modificationDate': datetime.now(),
        'plainText': plain_text,
        'snippetType': 0,
        'uuidString': str(uuid.uuid4()).upper()
    }


def get_ti4m():
    return {
        'Abbreviation': None,
        'CreatedBy': '',
        'Creation Date': datetime.now(),
        'DateLastUsed': datetime.now(),
        'Device': '',
        'Label': '',
        'Modification Date': datetime.now(),
        'Option': '',
        'Plain Text': None,
        'SortOrder': 1,
        'uuidString': str(uuid.uuid4()).upper()
    }


def get_ak(abbreviation=None, plain_text=None):
    return (
        {
            "usageCount": 0,
            "omitTrigger": True,
            "prompt": False,
            "description": getShortText(plain_text),
            "abbreviation": {
                "wordChars": "[^" + ak_default_trigger_char + "]",
                "abbreviations": [
                    abbreviation
                ],
                "immediate": False,
                "ignoreCase": False,
                "backspace": True,
                "triggerInside": False
            },
            "hotkey": {
                "hotKey": None,
                "modifiers": []
            },
            "modes": [
                1
            ],
            "showInTrayMenu": True,
            "matchCase": False,
            "filter": {
                "regex": None,
                "isRecursive": False
            },
            "type": "phrase",
            "sendMode": "kb"
        },
        abbreviation,
        plain_text
    )

def transform(direction, source):
    if direction == 'toTE':
        return get_te(abbreviation=source['Abbreviation'], plain_text=source['Plain Text'])
    elif direction == 'toAK':
        return get_ak(abbreviation=source['Abbreviation'], plain_text=source['Plain Text'])
    elif direction == 'toTI4M':
        pass
    else:
        raise Exception('Unsupported direction')

def getShortText(longtext):
    if len(longtext)<=20:
        return longtext
    else:
        return longtext[0:19]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Expander Sync')

    parser.add_argument('direction', choices=['toTE', 'toTI4M', 'toAK'])
    parser.add_argument('--te', default=None, help='TextExpander xml plist')
    parser.add_argument('--ti4m', default=None, help='TypeIt4Me xml plist')
    parser.add_argument('--ak', default=None, help='Autokey target dir')

    args = parser.parse_args()

    print(args.direction)

    source = args.te if args.direction == 'toTI4M' else args.ti4m
    if args.direction == 'toTI4M':
        target = args.ti4m
    if args.direction == 'toTE':
        target = args.te
    if args.direction == 'toAK':
        target = args.ak

    with open(source, 'rb') as source_fp:
        source_plist = readPlist(source_fp)

    converted_snippets = []

    for s in source_plist['Clippings']:
        converted_snippets.append(transform(args.direction, s))

    if args.direction == 'toAK':
        for snippit in converted_snippets:
            with io.open(target + '/.' + snippit[1] + '.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(snippit[0], indent=4, ensure_ascii=False))
            with io.open(target + '/' + snippit[1] + '.txt', 'w', encoding='utf-8') as f:
                f.write(snippit[2])
    else:
        with open(target, 'rb') as target_fp:
            target_plist = readPlist(target_fp)

            if args.direction == 'toTE':
                target_plist['snippetPlists'] = converted_snippets
            else:
                raise Exception('Unsupported')

        with open(target, 'wb') as target_fp:
            writePlist(target_plist, target_fp)
