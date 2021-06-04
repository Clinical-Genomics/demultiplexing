"""
    Constants for indexcheck report
"""


REFERENCE_REPORT_HEADER = [
    "Lane",
    "Project",
    "Sample",
    "Barcode sequence",
    "PF Clusters",
    "% of the lane",
    "% Perfect barcode",
    "% One mismatch barcode",
    "Yield (Mbases)",
    "% PF Clusters",
    "% &gt;= Q30 bases",
    "Mean Quality Score",
]

REPORT_TABLES_INDEX = {"cluster_count_table": 1, "top_unknown_barcode_table": 2}

FLOWCELL_VERSION_LANE_COUNT = {"S1": 2, "S2": 2, "SP": 2, "S4": 4}
