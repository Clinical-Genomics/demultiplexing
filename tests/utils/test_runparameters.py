""" Tests parsing of run parameters """

import mock
import pytest


def test_find_runparameters_file(novaseq_runparameters_api, novaseq_runs_dir):
    """ tests find runparameters_file method """
    result = novaseq_runparameters_api.find_runparameters_file()
    flowcell_id = novaseq_runparameters_api.flowcell
    assert result == str(novaseq_runs_dir) + "/test_run_dir_" + flowcell_id + "/RunParameters.xml"


def test_control_software_version_old_SCV(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests find runparameters_file method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_oldSCV"]
    result = novaseq_runparameters_api.control_software_version
    assert result == "1.6.0"


def test_control_software_version_new_SCV(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests control software version method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_newSCV_newkit"]
    result = novaseq_runparameters_api.control_software_version
    assert result == "1.7.0"


def test_control_software_version_index_reads_fluffy(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests control software version method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_fluffy"]
    result = novaseq_runparameters_api.index_reads
    assert result == 8


def test_index_reads(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests index reads method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_newSCV_newkit"]
    result = novaseq_runparameters_api.index_reads
    assert result == 10


def test_reagent_kit_new(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests reagent kit method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_newSCV_newkit"]
    result = novaseq_runparameters_api.reagent_kit_version
    assert result == "3"


def test_reagent_kit_old(novaseq_runparameters_api, novaseq_runs_dir, run_parameters_file):
    """ tests reagent kit method """
    api = novaseq_runparameters_api
    api.file =run_parameters_file["novaseq_newSCV_oldkit"]
    result = novaseq_runparameters_api.reagent_kit_version
    assert result == "1"
