#! /usr/bin/env python
import asyncio
import os
import sys
from functools import partial
from operator import itemgetter

from rx import Observable


def main(directory):
    non_hidden_files  = Observable.from_(os.fwalk('./'))\
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


def _diff(acc, curr):
    acc = set(map(lambda el: tuple(el.items()), acc)) 
    curr_temp = set(map(lambda el: tuple(el.items()), curr))

    changed_files = [*map(dict, acc.difference(curr_temp))]
    file_names = [*map(itemgetter('name'), changed_files)]

    if file_names:
        os.system('pytest')
        print("File(s) changed: ", *file_names, sep='\n', end='\n')

    return curr


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    print("Listening...")

    rate = int(sys.argv[1])

    sub = Observable.interval(rate)\
            .flat_map(lambda el: main('.'))\
            .distinct_until_changed()\
            .scan(_diff)\
            .subscribe(on_completed=lambda: _stop(loop))

    loop.run_forever()
    sub.dispose()

