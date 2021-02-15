import bs4

from pathlib import Path

from demux.utils.indexreport import IndexReport

from demux.utils.html import (
    get_html_content,
    parse_html_header,
    parse_html_project_cluster_counts,
)


def test_get_html_content(novaseq_valid_indexcheck_report: Path):
    """Test the function to retrieve html content from a path"""
    # GIVEN a html file
    # WHEN retrieving content from the file
    html_content = get_html_content(novaseq_valid_indexcheck_report)
    # THEN it should be a bs4.BeautifulSoup object
    assert type(html_content) is bs4.BeautifulSoup


def test_parse_html_header(indexreport_sample_table_header: bs4.element.Tag):
    """Test if the parsing function removes html code properly and returns a string"""
    # GIVEN a header from the cluster count sample table
    for html_column_header in indexreport_sample_table_header:
        # WHEN parsing this header and attempting to remove html syntax
        column_header = parse_html_header(html_column_header=html_column_header)
        # THEN we should get a string, and have no markers of html left
        assert type(column_header) is str
        assert ">" or "<" not in column_header


def test_parse_html_project_cluster_counts(
    indexreport_sample_table_row: bs4.element.Tag, valid_indexreport: IndexReport
):
    # GIVEN a row from a valid indexreport class
    # WHEN parsing a row from the sample cluster count table
    project, counts = parse_html_project_cluster_counts(
        header_index=valid_indexreport.sample_table_header,
        project_row=indexreport_sample_table_row,
    )
    # THEN we should retrieve a project and cluster count
    assert type(project) is str
    assert project == "257845"
    assert type(counts) is int
    assert counts == 4375049
