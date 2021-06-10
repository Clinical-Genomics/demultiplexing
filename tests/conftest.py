""" Conftest file for demultiplexing """
import shutil
from pathlib import Path
from typing import Dict

import pytest

from demux.utils.runparameters import NovaseqRunParameters


@pytest.fixture(scope="function", name="project_dir")
def tmp_dir(tmp_path_factory) -> Path:
    """Yield temp dir"""

    my_tmpdir = Path(tmp_path_factory.mktemp("data"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture(name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to the fixtures directory"""
    return Path("tests/fixtures")


@pytest.fixture(name="files_dir")
def fixture_analysis_dir(fixtures_dir: Path) -> Path:
    """Return the path to the files directory"""
    return fixtures_dir / "files"


@pytest.fixture(name="dummy_indexes_file")
def fixture_dummy_indexes_file(files_dir: Path) -> Path:
    """Fixture for the dummy index file"""
    return files_dir / "20181012_Indices.csv"


@pytest.fixture(name="novaseq_dir")
def fixture_novaseq_dir(fixtures_dir: Path) -> Path:
    """Return the path to the novaseq directory"""
    return fixtures_dir / "novaseq"


@pytest.fixture(name="hiseqx_samplesheet_pooled_path")
def fixture_hiseqx_samplesheet_pooled_path(hiseqx_dir: Path) -> Path:
    """Return the path to a pooled HiSeqX samplesheet"""
    return hiseqx_dir / "hiseqx_samplesheet_pooled.csv"


@pytest.fixture(name="hiseq2500_dir")
def fixture_2500_dir(fixtures_dir: Path) -> Path:
    """Return the path to the 2500 directory"""
    return fixtures_dir / "2500"


@pytest.fixture(name="novaseq_valid_indexcheck_report")
def fixture_novaseq_valid_indexcheck_report(novaseq_dir: Path) -> Path:
    """Return the path to valid indexcheck report"""
    return novaseq_dir / "valid_laneBarcode.html"


@pytest.fixture(name="novaseq_indexcheck_wrong_header_rt1")
def fixture_novaseq_invalid_rt1_indexcheck_report(novaseq_dir: Path) -> Path:
    """Return the path to valid indexcheck report"""
    return novaseq_dir / "wrong_header_rt1.html"


@pytest.fixture(name="novaseq_indexcheck_invalid_rt2")
def fixture_novaseq_invalid_rt2_indexcheck_report(novaseq_dir: Path) -> Path:
    """Return the path to valid indexcheck report"""
    return novaseq_dir / "indexcheck_invalid_rt2.html"


@pytest.fixture(name="s1_run_parameters")
def fixture_s1_run_parameters(novaseq_dir: Path) -> Path:
    """Return the path to a S! RunParameters.xml"""
    return novaseq_dir / "S1_RunParameters.xml"


@pytest.fixture(name="s4_run_parameters")
def fixture_s4_run_parameters(novaseq_dir: Path) -> Path:
    """Return the path to a S! RunParameters.xml"""
    return novaseq_dir / "S4_RunParameters.xml"


@pytest.fixture(name="novaseq_runs_dir")
def fixture_runs_dir(novaseq_dir: Path) -> Path:
    """Return the path to the novaseq runs directory"""
    return novaseq_dir / "runs"


@pytest.fixture(name="hiseqx_dir")
def fixture_hisex_dir(fixtures_dir: Path) -> Path:
    """Return the path to the hiseqx fixture directory"""
    return fixtures_dir / "hiseqx"


@pytest.fixture(name="hiseqx_samplesheet_path")
def fixture_hiseqx_samplesheet(hiseqx_dir: Path) -> Path:
    """Return the path to a hiseqx samplesheet"""
    return hiseqx_dir / "hiseqx_samplesheet.csv"


@pytest.fixture(name="hiseqx_samplesheet_wrong_columns_path")
def fixture_hiseqx_samplesheet_wrong_columns_path(hiseqx_dir: Path) -> Path:
    """Return the path to a hiseqx samplesheet with wrong columns"""
    return hiseqx_dir / "hiseqx_samplesheet_wrong_columns.csv"


@pytest.fixture(name="hiseqx_samplesheet_multiple_indexes_path")
def fixture_hiseqx_samplesheet_multiple_indexes_path(hiseqx_dir: Path) -> Path:
    """Return the path to a hiseqx samplesheet with multiple indexes types"""
    return hiseqx_dir / "hiseqx_samplesheet_multiple_index.csv"


@pytest.fixture(name="nipt_dir")
def fixture_nipt_dir(fixtures_dir: Path) -> Path:
    """Return the path to nipt fixture directory"""
    return fixtures_dir / "nipt"


@pytest.fixture(name="nipt_samplesheet_path")
def fixture_nipt_samplesheet_path(nipt_dir: Path) -> Path:
    """Return path to nipt samplesheet"""
    return nipt_dir / "nipt_samplesheet.csv"


@pytest.fixture(name="nipt_faulty_samplesheet_path")
def fixture_nipt_faulty_samplesheet_path(nipt_dir: Path) -> Path:
    """Return path to a faulty nipt samplesheet"""
    return nipt_dir / "nipt_faulty_samplesheet.csv"


@pytest.fixture(name="hiseq2500_dir")
def fixture_hiseq2500_dir(fixtures_dir: Path) -> Path:
    """Return path to the 2500 fixture directory"""
    return fixtures_dir / "2500"


@pytest.fixture(name="run_parameters_file")
def fixture_novaseq_runparameters_file(novaseq_runs_dir: Path) -> Dict[str, Path]:
    """Fixture for novaseq runparameters files"""
    return {
        "novaseq_oldSCV": novaseq_runs_dir / "RunParameters_oldSCV.xml",
        "novaseq_newSCV_oldkit": novaseq_runs_dir / "RunParameters_newSCV_oldkit.xml",
        "novaseq_newSCV_newkit": novaseq_runs_dir / "RunParameters_newSCV_newkit.xml",
        "novaseq_fluffy": novaseq_runs_dir / "RunParameters_fluffy.xml",
    }


@pytest.fixture(scope="function", name="novaseq_runparameters_api")
def fixture_novaseq_runparameters_api(novaseq_runs_dir: Path):
    """Set up novaseq runparameters api for testing"""
    novaseq_runparameters_api = NovaseqRunParameters(
        "HGJJKDSXY", novaseq_runs_dir.as_posix()
    )
    return novaseq_runparameters_api
