""" Tests parsing of run parameters """
import pytest


def test_find_runparameters_file(novaseq_runparameters_api, novaseq_runs_dir):
    """ tests find runparameters_file method """

    # GIVEN a flowcell id
    flowcell_id = novaseq_runparameters_api.flowcell

    # WHEN a runs folder exists for the flowcell
    result = novaseq_runparameters_api.find_runparameters_file()

    # THEN a RunParameters.xml should be found for the run of thay flowcell
    assert (
        result
        == str(novaseq_runs_dir) + "/test_run_dir_" + flowcell_id + "/RunParameters.xml"
    )


def test_find_runparameters_file_not_found(novaseq_runparameters_api):
    """ tests find runparameters_file method """

    # GIVEN a flowcell id
    novaseq_runparameters_api.flowcell = "NO_FLOWCELL"
    flowcell_id = novaseq_runparameters_api.flowcell

    # WHEN a runs folder does not exist for the flowcell
    with pytest.raises(Exception) as exc_info:
        novaseq_runparameters_api.find_runparameters_file()

    # THEN a RunParameters.xml should be found for the run of thay flowcell
    assert str(exc_info.value) == f"Run parameters for flowcell {flowcell_id} not found!"


def test_control_software_version_old_scv(
    novaseq_runparameters_api, run_parameters_file
):
    """ tests find runparameters_file method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the old software control version
    api.file = run_parameters_file["novaseq_oldSCV"]
    result = novaseq_runparameters_api.control_software_version

    # THEN the method should return the version for the old control software
    assert result == "1.6.0"


def test_control_software_version_new_scv(
    novaseq_runparameters_api, run_parameters_file
):
    """ tests control software version method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the new software control version
    api.file = run_parameters_file["novaseq_newSCV_newkit"]
    result = novaseq_runparameters_api.control_software_version

    # THEN the method should return the version for the new control software
    assert result == "1.7.0"


def test_control_software_version_index_reads_fluffy(
    novaseq_runparameters_api, run_parameters_file
):
    """ tests control software version method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the number of index reads for a NovaSeq (NIPT) run
    api.file = run_parameters_file["novaseq_fluffy"]
    result = novaseq_runparameters_api.index_reads

    # THEN the method should return the correct number of reads, 8
    assert result == 8


def test_index_reads(novaseq_runparameters_api, run_parameters_file):
    """ tests index reads method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the number of index reads for a NovaSeq run
    api.file = run_parameters_file["novaseq_newSCV_newkit"]
    result = novaseq_runparameters_api.index_reads

    # THEN the method should return the correct number of reads, 10
    assert result == 10


def test_reagent_kit_new(novaseq_runparameters_api, run_parameters_file):
    """ tests reagent kit method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the reagent kit version of a run using the new reagent
    # kit
    api.file = run_parameters_file["novaseq_newSCV_newkit"]

    # THEN the method should return '3'
    result = novaseq_runparameters_api.reagent_kit_version
    assert result == "3"


def test_reagent_kit_old(novaseq_runparameters_api, run_parameters_file):
    """ tests reagent kit method """

    # GIVEN an instance of the runparameters API
    api = novaseq_runparameters_api

    # WHEN parsing the RunParameters.xml for the reagent kit version of a run using the old reagent
    # kit
    api.file = run_parameters_file["novaseq_newSCV_oldkit"]
    result = novaseq_runparameters_api.reagent_kit_version

    # THEN the method should return '1'
    assert result == "1"
