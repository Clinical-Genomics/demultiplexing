""" Conftest file for demultiplexing """
from pathlib import Path
import pytest

from demux.utils.runparameters import NovaseqRunParameters
from demux.utils.samplesheet import HiSeqXSamplesheet


@pytest.fixture(name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """ Return the path to the fixtures directory """
    return Path("tests/fixtures")


@pytest.fixture(name="files_dir")
def fixture_analysis_dir(fixtures_dir: Path) -> Path:
    """ Return the path to the files directory """
    return fixtures_dir / "files"


@pytest.fixture(name="dummy_indexes_file")
def fixture_dummy_indexes_file(files_dir: Path) -> Path:
    """ Fixture for the dummy index file """
    return files_dir / "20181012_Indices.csv"


@pytest.fixture(name="novaseq_dir")
def fixture_novaseq_dir(fixtures_dir: Path) -> Path:
    """ Return the path to the novaseq directory """
    return fixtures_dir / "novaseq"


@pytest.fixture(name="novaseq_runs_dir")
def fixture_runs_dir(novaseq_dir: Path) -> Path:
    """ Return the path to the novaseq runs directory """
    return novaseq_dir / "runs"


@pytest.fixture(name="hiseqx_samplesheet_multiple_index")
def fixture_hiseqx_samplesheet_multiple_index(fixtures_dir: Path) -> HiSeqXSamplesheet:
    """ Return a hiseqx sample sheet containing multiple indexes """
    hiseqx_samplesheet_multiple_index = HiSeqXSamplesheet(fixtures_dir / "x_samplesheet_multiple_index.csv")

    return hiseqx_samplesheet_multiple_index


@pytest.fixture(name="run_parameters_file")
def fixture_novaseq_runparameters_file(novaseq_runs_dir: Path) -> Path:
    """ Fixture for novaseq runparameters files """
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
    """ Set up novaseq runparameters api for testing """
    novaseq_runparameters_api = NovaseqRunParameters("HGJJKDSXY", novaseq_runs_dir)
    return novaseq_runparameters_api
