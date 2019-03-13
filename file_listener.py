import asyncio
import os
from functools import partial
from collections import Counter
from itertools import chain
from operator import itemgetter

from rx import Observable


def main(directory):
    files = os.scandir(directory)
    return Observable.from_(files)\
            .map(lambda f: {'name': f.name, 'size': f.stat().st_size})\
            .to_list()\
            .finally_action(lambda: files.close())


def _stop(loop):
    loop.call_soon_threadsafe(loop.stop)


def _diff(acc, curr):
    acc = set(map(lambda el: tuple(el.items()), acc)) 
    curr_temp = set(map(lambda el: tuple(el.items()), curr))

    changed_files = [*map(dict, acc.difference(curr_temp))]
    file_names = [*map(itemgetter('name'), changed_files)]
    print("File(s) changed: ", *file_names, sep='\n', end='\n')
    return curr


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    print("Listening...")

    sub = Observable.interval(1000)\
            .flat_map(lambda el: main('./'))\
            .distinct_until_changed()\
            .scan(_diff)\
            .subscribe(on_completed=lambda: _stop(loop))

    loop.run_forever()
    sub.dispose()

