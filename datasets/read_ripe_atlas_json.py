#!/usr/bin/env python3

#########
# transform JSON file from RIPE Atlas into a friendly format
# example: input file: 201602071400.json
#          output file: 201602071400_formatted.txt
#########

from optparse import OptionParser
import json
from pprint import pprint


def main():
    parser = OptionParser(usage="usage: %prog filename", version="%prog 1.0")
    options, args = parser.parse_args()

    if len(args) != 1:
        print("you should enter 1 argument")
        return 1

    with open(args[0], 'r') as input_file:
        with open(args[0].strip('.json') + "_formatted.txt", 'w') as output_file:
            json_data = json.load(input_file)
            pprint(json_data, stream=output_file)

if __name__ == '__main__':
    main()