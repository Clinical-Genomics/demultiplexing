""" Conftest file for demultiplexing """
from pathlib import Path
from typing import Dict

import pytest
import shutil

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


@pytest.fixture(name="run_parameters_file")
def fixture_novaseq_runparameters_file(novaseq_runs_dir: Path) -> Dict[str, Path]:
    """Fixture for novaseq runparameters files"""
    return {
        "novaseq_oldSCV": novaseq_runs_dir
        / "RunParameters_oldSCV.xml",  # TODO: choose proper name
        "novaseq_newSCV_oldkit": novaseq_runs_dir
        / "RunParameters_newSCV_oldkit.xml",  # TODO: choose proper name
        "novaseq_newSCV_newkit": novaseq_runs_dir
        / "RunParameters_newSCV_newkit.xml",  # TODO: choose proper name
        "novaseq_fluffy": novaseq_runs_dir
        / "RunParameters_fluffy.xml",  # TODO: choose proper name
    }


@pytest.yield_fixture(scope="function", name="novaseq_runparameters_api")
def fixture_novaseq_runparameters_api(novaseq_runs_dir):
    """Set up novaseq runparameters api for testing"""
    novaseq_runparameters_api = NovaseqRunParameters("HGJJKDSXY", novaseq_runs_dir)
    return novaseq_runparameters_api
