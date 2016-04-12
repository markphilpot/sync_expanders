import argparse
from plistlib import readPlist, writePlist

import uuid
from datetime import datetime


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


def transform(direction, source):
    if direction == 'toTE':
        return get_te(abbreviation=source['Abbreviation'], plain_text=source['Plain Text'])
    elif direction == 'toTI4M':
        pass
    else:
        raise Exception('Unsupported direction')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Expander Sync')

    parser.add_argument('direction', choices=['toTE', 'toTI4M'])
    parser.add_argument('--te', default=None, help='TextExpander xml plist')
    parser.add_argument('--ti4m', default=None, help='TypeIt4Me xml plist')

    args = parser.parse_args()

    print(args.direction)

    source = args.te if args.direction == 'toTI4M' else args.ti4m
    target = args.ti4m if args.direction == 'toTI4M' else args.te

    with open(source, 'rb') as source_fp:
        source_plist = readPlist(source_fp)

    converted_snippets = []

    for s in source_plist['Clippings']:
        converted_snippets.append(transform(args.direction, s))

    with open(target, 'rb') as target_fp:
        target_plist = readPlist(target_fp)

        if args.direction == 'toTE':
            target_plist['snippetPlists'] = converted_snippets
        else:
            raise Exception('Unsupported')

    with open(target, 'wb') as target_fp:
        writePlist(target_plist, target_fp)