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
