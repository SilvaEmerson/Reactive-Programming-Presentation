#! /usr/bin/env python
import asyncio
import os
import sys
from functools import partial
from operator import itemgetter
import argparse

from rx import Observable


def main(directory):
    non_hidden_files  = Observable.from_(os.fwalk(directory))\
            .filter(lambda el: not el[0].startswith('./.'))\


    return non_hidden_files.flat_map(lambda val: Observable.from_(val[2])\
            .map(lambda el: os.path.join(val[0], el)))\
            .map(lambda el: {
                'name': el,
                'size': os.stat(el).st_size
                })\
            .to_list()\


def _stop(loop):
    loop.call_soon_threadsafe(loop.stop)


def _diff(command, acc, curr):
    acc = set(map(lambda el: tuple(el.items()), acc)) 
    curr_temp = set(map(lambda el: tuple(el.items()), curr))

    changed_files = [*map(dict, acc.difference(curr_temp))]
    file_names = [*map(itemgetter('name'), changed_files)]

    if file_names:
        os.system(command)
        print("File(s) changed: ", *file_names, sep='\n', end='\n')

    return curr


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    parser = argparse.ArgumentParser()
    required = parser.add_argument_group("required arguments")

    required.add_argument(
        "--rate",
        metavar="N ms",
        type=int,
        required=True,
        help="The ms refreshing rate",
    )

    required.add_argument(
        "--command",
        metavar="CMD",
        type=str,
        required=True,
        help="The that will run after any file change in file tree",
    )

    params = vars(parser.parse_args())

    rate = params.get("rate")
    command = params.get("command")

    print("Listening...")

    sub = Observable.interval(rate)\
            .flat_map(lambda el: main('.'))\
            .distinct_until_changed()\
            .scan(partial(_diff, command))\
            .subscribe(on_completed=lambda: _stop(loop))

    loop.run_forever()
    sub.dispose()

