"""
    Constants for indexcheck report
"""


reference_report_header = [
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

report_tables_index = {"cluster_count_table": 1, "top_unknown_barcode_table": 2}

flowcell_version_lane_count = {"S1": 2, "S4": 4}
