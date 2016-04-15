#!/usr/bin/env python3

import json
from optparse import OptionParser


def main():
    parser = OptionParser(usage="usage: %prog filename", version="%prog 1.0")
    options, args = parser.parse_args()

    if len(args) != 1:
        print("you should enter 1 argument")
        return 1

    with open(args[0], 'r') as input_file:
        json_data = json.load(input_file)

    success_trace = 0       # counter
    unsuccess_trace = 0     # counter
    probe_list = []

    for probe in json_data:
        probe_list.append(probe['prb_id'])
        if 'result' in probe:
            if all('x' in result or 'err' in result for result in probe['result'][-1]['result']):
                unsuccess_trace += 1
            else:
                success_trace += 1
                print('probe {} reaches target'.format(probe['prb_id']))

    unique_probe_list = set(probe_list)
    print('\nTotal probes: {}\nProbe list:\n{}'.format(len(unique_probe_list), list(unique_probe_list)))
    print('\nSuccessful traceroutes: {} \nUnsuccessful traceroutes: {}'.format(success_trace, unsuccess_trace))

if __name__ == '__main__':
    main()