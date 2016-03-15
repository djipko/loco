#!/usr/bin/env python3

import re
import heapq
import sys


class Pushable:
    def __init__(self, iterable):
        self.iterable = iterable
        self.pushed = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.pushed is not None:
            r = self.pushed
            self.pushed = None
            return r

        return next(self.iterable)

    def push(self, item):
        self.pushed = item


class LogChunk:
    def __init__(self, filename, comparator, lines):
        self.comparator = comparator
        self.lines = lines
        self.filename = filename

    def __lt__(self, other):
        return self.comparator < other.comparator

    def __str__(self):
        prefix = self.filename + ': '
        return prefix + prefix.join(self.lines)


class LogFile:
    TIMESTAMP = re.compile('^[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}$')

    def __init__(self, filename):
        self.filename = filename
        self.f = Pushable(open(filename))
        self.sort_field = self.line = None

    def __lt__(self, other):
        return self.sort_field < other.sort_field

    def __iter__(self):
        return self

    def __next__(self):
        lines = []
        ts = None
        for line in self.f:
            fields = line.split(' ')

            # First line of a chunk
            if ts is None:
                if len(fields) >= 2 and self.TIMESTAMP.match(fields[1]):
                    ts = (fields[0], fields[1])
                else:
                    # Discard leading lines with no timestamp
                    continue

            # Chunk lines from a single log file with the same timestamp
            elif len(fields) >= 2 and ts != (fields[0], fields[1]):
                # Might be non-timestamped continuation line
                if self.TIMESTAMP.match(fields[1]):
                    # This is the next line, so push it back
                    self.f.push(line)
                    break

            lines.append(line)

        if len(lines) == 0:
            raise StopIteration()

        return LogChunk(self.filename, ts, lines)


class LoCo:
    """Combine sorted log files into a single stream"""
    def __init__(self, filenames, logfile_class=LogFile):
        self.files = [logfile_class(filename) for filename in filenames]

    def __iter__(self):
        return heapq.merge(*self.files)


if __name__ == "__main__":
    loco = LoCo(sys.argv[1:])
    for line in loco:
        sys.stdout.write(str(line))
