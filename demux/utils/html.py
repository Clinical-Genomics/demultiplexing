import re
import bs4

from pathlib import Path


def parse_html_header(html_column_header: bs4.element.Tag) -> str:
    """Purify html header into a string without html syntax"""

    column_header = re.sub("<br/>", " ", str(html_column_header))
    header = re.sub("<.*?>", "", column_header)

    return header


def parse_html_project_cluster_counts(
    header_index: dict, project_row: bs4.element.Tag
) -> (str, int):
    """Purify a html project cluster count row from html syntax"""

    project = re.sub(
        "<.*?>", "", str(project_row.find_all("td")[header_index["Project"]])
    )
    cluster_count = re.sub(
        "<.*?>", "", str(project_row.find_all("td")[header_index["PF Clusters"]])
    )
    cluster_count = int(cluster_count.replace(",", ""))

    return project, cluster_count


def get_html_content(index_report_path: Path) -> bs4.BeautifulSoup:
    """Get the content of the report"""

    with index_report_path.open() as f:
        html_content = bs4.BeautifulSoup(f, "html.parser")
        return html_content


def get_report_tables(html_content: bs4.BeautifulSoup) -> bs4.ResultSet:
    """Get the ReportTables inside the html report"""

    report_tables = html_content.find_all("table", id="ReportTable")
    return report_tables


def get_sample_table_header(
    report_tables: bs4.ResultSet, report_tables_index: dict
) -> dict:
    """Get the header from the large table with all sample clusters"""

    header_index = {}

    html_sample_headers = report_tables[
        report_tables_index["cluster_count_table"]
    ].tr.find_all("th")

    for index, html_column_header in enumerate(html_sample_headers):
        header = parse_html_header(html_column_header)
        header_index[header] = index

    return header_index


def get_low_cluster_counts(
    cluster_counts: int,
    report_tables: bs4.ResultSet,
    report_tables_index: dict,
    sample_table_header: dict
) -> list:
    """Find samples with low cluster counts"""

    low_cluster_counts = []

    for html_project_cluster_count in report_tables[
        report_tables_index["cluster_count_table"]
    ].find_all("tr")[1:]:
        project, cluster_count = parse_html_project_cluster_counts(
            project_row=html_project_cluster_count,
            header_index=sample_table_header,
        )
        if project != "indexcheck":
            if cluster_count < cluster_counts:
                low_cluster_counts.append(html_project_cluster_count)

    return low_cluster_counts


def get_top_unknown_barcodes_table(
    report_tables: bs4.ResultSet, report_tables_index: dict
) -> bs4.element.Tag:
    """Get the table with the top unknown barcodes"""

    return report_tables[report_tables_index["top_unknown_barcode_table"]]
