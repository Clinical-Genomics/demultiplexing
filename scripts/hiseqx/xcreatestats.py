#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import xml.etree.ElementTree as et
import sys
import glob

__version__ = '3.6.1'

def xpathsum(tree, xpath):
    """TODO: Docstring for xpathsum.

    Args:
        et (TODO): TODO
        xpath (TODO): TODO

    Returns: TODO

    """
    numbers = tree.findall(xpath)
    return sum([ int(number.text) for number in numbers ])

def get_summary(tree):
    """TODO: Docstring for get_summary.

    Args:
        tree (TODO): TODO

    Returns: TODO

    """
    raw_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/ClusterCount")
    pf_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/ClusterCount")

    pf_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/Yield")
    raw_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/Yield")
    pf_clusters_pc = pf_yield / raw_yield

    pf_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/YieldQ30")
    raw_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/YieldQ30")
    pf_q30_bases_pc = pf_q30 / pf_yield

    pf_qscore_sum = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/QualityScoreSum")
    pf_qscore = pf_qscore_sum / pf_yield

    return {
        'raw_clusters': raw_clusters,
        'pf_clusters': pf_clusters,
        'pf_yield': pf_yield,
        'raw_yield': raw_yield,
        'pf_clusters_pc': pf_clusters_pc,
        'pf_q30': pf_q30,
        'raw_q30': raw_q30,
        'pf_q30_bases_pc': pf_q30_bases_pc,
        'pf_qscore_sum': pf_qscore_sum,
        'pf_qscore': pf_qscore
    }

def get_lanes(rundir):
    """Get the lanes from the SampleSheet

    Args:
        rundir (path): TODO

    Returns:
        a list of lane numbers

    """
    with open(rundir + '/SampleSheet.csv') as sample_sheet:
        lines = [ line.strip().split(',') for line in sample_sheet.readlines() ]
        return [ line[1] for line in lines[2:] ] # remove headers

def main(argv):
    """TODO: Docstring for main.

    Args:
        argv[0] (str): the RUNDIR

    """

    lanes = get_lanes(argv[0])
    # create a { 1: [], 2: [], ... } structure
    summaries = dict(zip(lanes, [ [] for t in xrange(len(lanes))])) # init ;)

    # get all the stats numbers
    for lane in lanes:
        stats_files = glob.glob('%s/l%st??/Stats/ConversionStats.xml' % (argv[0], lane))
        for i, f in enumerate(stats_files):
            tree = et.parse(f)
            summaries[ lane ].append(get_summary(tree))
    
    # sum the numbers over a lane
    # create a { 1: {'raw_clusters': 0, ... } } structure
    total_lane_summary = dict(zip(lanes, [ {
        'raw_clusters': 0,
        'pf_clusters': 0,
        'pf_yield': 0,
        'raw_yield': 0,
        'pf_clusters_pc': 0,
        'pf_q30': 0,
        'raw_q30': 0,
        'pf_q30_bases_pc': 0,
        'pf_qscore_sum': 0,
        'pf_qscore': 0 } for t in xrange(len(lanes))]))
    for lane, summary in summaries.items():
        for summary_quart in summary:
            for key, stat in summary_quart.items():
                total_lane_summary[lane][ key ] += stat

    # print me a pretty report
    print('\t'.join(('Lane', 'Raw_clusters', 'PF_clusters', 'Yield_MBases', '%_PF_Clusters', '%_>=_Q30_bases', 'Mean_Quality_Score')))
    for lane, summary in total_lane_summary.items():
        print('\t'.join( [
            lane,
            str(summary['raw_clusters']),
            str(summary['pf_clusters']),
            str(round(summary['pf_yield'] / 1000000, 0)),
            str(round(summary['pf_yield'] / summary['raw_yield'] * 100, 2)),
            str(round(summary['pf_q30'] / summary['pf_yield'] * 100, 2)),
            str(round(summary['pf_qscore_sum'] / summary['pf_yield'], 2))
        ]))

if __name__ == '__main__':
    main(sys.argv[1:])
