#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys
from datetime import datetime

def main(argv):

    lanes = {}
    for fn in argv:
        f = open(fn)
        lines = ( line.strip() for line in f.readlines() )

        lane_id = ''
        time_points = ('start copying','starting demultiplexing','starting copy output','Done copying output','Done removing')
        times = {}

        for line in lines:

            l = line.partition(' ')
            for time_point in time_points:
                if l[2].startswith(time_point):
                    times[time_point] = datetime.strptime(l[0].strip('[]'), '%Y%m%d%H%M%S')

                if l[2].startswith('starting demultiplexing'):
                    lane_id = l[2].partition('lane')[2]

        lanes[lane_id] = times

        print('%s:' % lane_id, end='')
        if 'start copying' in times:
            prev_time = times['start copying']
            for time_point in time_points:
                if time_point in times:
                    time = times[time_point]
                    diff = time - prev_time

                    elapsed_time = divmod(diff.days * 86400 + diff.seconds, 60)
                    print('%dm%d' % elapsed_time, end='\t')
                else:
                    print('', end='\t')

                prev_time = time
            print()

if __name__ == '__main__':
    main(sys.argv[1:])
