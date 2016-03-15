#!/usr/bin/env python3

import heapq
import sys


class LogFile:
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename)
        self.sort_field = self.line = None
        self.done = False
        next(self)

    def __cmp__(self, other):
        return cmp(self.sort_field, other.sort_field)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            line = next(self.f)
        except StopIteration:
            self.done = True
            raise
        self.sort_field = self.sort_field_from_line(line)
        self.line = self.process_line(line)
        return self.line

    def process_line(self, line):
        """Can be overriden to make changes to a line"""
        return " ".join((self.filename, line))

    def sort_field_from_line(self, line):
        """Can be overriden to generate a different sort field"""
        parts = line.split(" ")
        return " ".join((parts[0], parts[1]))


class LoCo:
    """Combine sorted log files into a single stream"""
    def __init__(self, filenames, logfile_class=LogFile):
        self.files = [logfile_class(filename) for filename in filenames]
        heapq.heapify(self.files)

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next line of combined log files"""
        if not self.files:
            raise StopIteration()
        next_f = heapq.heappop(self.files)
        line = next_f.line
        try:
            next(next_f)
        except StopIteration:
            return line
        else:
            heapq.heappush(self.files, next_f)
            return line


if __name__ == "__main__":
    loco = LoCo(sys.argv[1:])
    for line in loco:
        sys.stdout.write(line)
