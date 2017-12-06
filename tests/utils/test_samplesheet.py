#!/usr/bin/env python
# -*- coding: utf-8 -*-

from demux.utils import Samplesheet, NIPTSamplesheet, HiSeq2500Samplesheet, MiseqSamplesheet, SampleSheetValidationException
import pytest

def test_nipt_samplesheet():
    samplesheet = NIPTSamplesheet('tests/fixtures/nipt_samplesheet.csv')

    assert samplesheet._get_flowcell() == 'HFNC5BCXY'
    assert samplesheet._get_project_id() == '666666'
    assert samplesheet.raw() == """[Header],,,,,,,,,,
IEMFileVersion,4,,,,,,,,,
Investigator Name,9999999_666666,,,,,,,,,
Experiment Name,HFNC5BCXY,,,,,,,,,
Date,3/14/17,,,,,,,,,
Workflow,GenerateFASTQ,,,,,,,,,
Application,HiSeq FASTQ Only,,,,,,,,,
Assay,TruSeq LT,,,,,,,,,
Description,cfDNAHiSeqv1.0 ,,,,,,,,,
Chemistry,Default,,,,,,,,,
,,,,,,,,,,
[Reads],,,,,,,,,,
36,,,,,,,,,,
,,,,,,,,,,
[Settings],,,,,,,,,,
,,,,,,,,,,
[Data],,,,,,,,,,
Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,Sample_Project,Description,SampleType,Library_nM
1,test-1705166-05,test-1705166-05,,A2,A002,CGATGT,,,Test,69.07001045
1,test-1705169-05,test-1705169-05,,B2,A005,ACAGTG,,,Test,62.27795193
1,test-1705170-05,test-1705170-05,,C2,A007,CAGATC,,,Test,58.51619645
1,test-1705183-06,test-1705183-06,,D2,A012,CTTGTA,,,Test,49.11180773
1,test-1705225-05,test-1705225-05,,E2,A013,AGTCAA,,,Test,80.66875653
1,test-1705258-05,test-1705258-05,,F2,A014,AGTTCC,,,Test,61.96447231
1,test-1705259-05,test-1705259-05,,G2,A018,GTCCGC,,,Test,86.20689655
1,test-1705266-05,test-1705266-05,,H2,A019,GTGAAA,,,Test,54.44096134
1,test-1705355-05,test-1705355-05,,A4,A001,ATCACG,,,Test,80.77324974
1,test-1705387-05,test-1705387-05,,B4,A003,TTAGGC,,,Test,81.19122257
1,test-1705388-05,test-1705388-05,,C4,A008,ACTTGA,,,Test,79.41483804
1,test-1705398-06,test-1705398-06,,D4,A010,TAGCTT,,,Test,66.24869383
1,test-1705431-05,test-1705431-05,,E4,A020,GTGGCC,,,Test,74.08568443
1,test-1705432-05,test-1705432-05,,F4,A022,CGTACG,,,Test,79.83281087
1,PCS-1724772-01,PCS-1724772-01,,G4,A025,ACTGAT,,,Control,76.07105538
2,test-1705166-05,test-1705166-05,,A2,A002,CGATGT,,,Test,69.07001045
2,test-1705169-05,test-1705169-05,,B2,A005,ACAGTG,,,Test,62.27795193
2,test-1705170-05,test-1705170-05,,C2,A007,CAGATC,,,Test,58.51619645
2,test-1705183-06,test-1705183-06,,D2,A012,CTTGTA,,,Test,49.11180773
2,test-1705225-05,test-1705225-05,,E2,A013,AGTCAA,,,Test,80.66875653
2,test-1705258-05,test-1705258-05,,F2,A014,AGTTCC,,,Test,61.96447231
2,test-1705259-05,test-1705259-05,,G2,A018,GTCCGC,,,Test,86.20689655
2,test-1705266-05,test-1705266-05,,H2,A019,GTGAAA,,,Test,54.44096134
2,test-1705355-05,test-1705355-05,,A4,A001,ATCACG,,,Test,80.77324974
2,test-1705387-05,test-1705387-05,,B4,A003,TTAGGC,,,Test,81.19122257
2,test-1705388-05,test-1705388-05,,C4,A008,ACTTGA,,,Test,79.41483804
2,test-1705398-06,test-1705398-06,,D4,A010,TAGCTT,,,Test,66.24869383
2,test-1705431-05,test-1705431-05,,E4,A020,GTGGCC,,,Test,74.08568443
2,test-1705432-05,test-1705432-05,,F4,A022,CGTACG,,,Test,79.83281087
2,PCS-1724772-01,PCS-1724772-01,,G4,A025,ACTGAT,,,Control,76.07105538"""

    samplesheet_lines = [ line for line in samplesheet.lines() ]
    assert samplesheet_lines == [
        {'index': 'CGATGT', 'lane': '1', 'description': '', 'sample_id': 'test-1705166-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A002', 'sample_well': 'A2', 'sample_project': '', 'library_nm': '69.07001045', 'sample_name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'lane': '1', 'description': '', 'sample_id': 'test-1705169-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A005', 'sample_well': 'B2', 'sample_project': '', 'library_nm': '62.27795193', 'sample_name': 'test-1705169-05'},
        {'index': 'CAGATC', 'lane': '1', 'description': '', 'sample_id': 'test-1705170-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A007', 'sample_well': 'C2', 'sample_project': '', 'library_nm': '58.51619645', 'sample_name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'lane': '1', 'description': '', 'sample_id': 'test-1705183-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A012', 'sample_well': 'D2', 'sample_project': '', 'library_nm': '49.11180773', 'sample_name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'lane': '1', 'description': '', 'sample_id': 'test-1705225-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A013', 'sample_well': 'E2', 'sample_project': '', 'library_nm': '80.66875653', 'sample_name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'lane': '1', 'description': '', 'sample_id': 'test-1705258-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A014', 'sample_well': 'F2', 'sample_project': '', 'library_nm': '61.96447231', 'sample_name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'lane': '1', 'description': '', 'sample_id': 'test-1705259-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A018', 'sample_well': 'G2', 'sample_project': '', 'library_nm': '86.20689655', 'sample_name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'lane': '1', 'description': '', 'sample_id': 'test-1705266-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A019', 'sample_well': 'H2', 'sample_project': '', 'library_nm': '54.44096134', 'sample_name': 'test-1705266-05'},
        {'index': 'ATCACG', 'lane': '1', 'description': '', 'sample_id': 'test-1705355-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A001', 'sample_well': 'A4', 'sample_project': '', 'library_nm': '80.77324974', 'sample_name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'lane': '1', 'description': '', 'sample_id': 'test-1705387-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A003', 'sample_well': 'B4', 'sample_project': '', 'library_nm': '81.19122257', 'sample_name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'lane': '1', 'description': '', 'sample_id': 'test-1705388-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A008', 'sample_well': 'C4', 'sample_project': '', 'library_nm': '79.41483804', 'sample_name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'lane': '1', 'description': '', 'sample_id': 'test-1705398-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A010', 'sample_well': 'D4', 'sample_project': '', 'library_nm': '66.24869383', 'sample_name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'lane': '1', 'description': '', 'sample_id': 'test-1705431-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A020', 'sample_well': 'E4', 'sample_project': '', 'library_nm': '74.08568443', 'sample_name': 'test-1705431-05'},
        {'index': 'CGTACG', 'lane': '1', 'description': '', 'sample_id': 'test-1705432-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A022', 'sample_well': 'F4', 'sample_project': '', 'library_nm': '79.83281087', 'sample_name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'lane': '1', 'description': '', 'sample_id': 'PCS-1724772-01', 'sample_type': 'Control', 'sample_plate': '', 'i7_index_id': 'A025', 'sample_well': 'G4', 'sample_project': '', 'library_nm': '76.07105538', 'sample_name': 'PCS-1724772-01'},
        {'index': 'CGATGT', 'lane': '2', 'description': '', 'sample_id': 'test-1705166-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A002', 'sample_well': 'A2', 'sample_project': '', 'library_nm': '69.07001045', 'sample_name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'lane': '2', 'description': '', 'sample_id': 'test-1705169-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A005', 'sample_well': 'B2', 'sample_project': '', 'library_nm': '62.27795193', 'sample_name': 'test-1705169-05'},
        {'index': 'CAGATC', 'lane': '2', 'description': '', 'sample_id': 'test-1705170-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A007', 'sample_well': 'C2', 'sample_project': '', 'library_nm': '58.51619645', 'sample_name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'lane': '2', 'description': '', 'sample_id': 'test-1705183-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A012', 'sample_well': 'D2', 'sample_project': '', 'library_nm': '49.11180773', 'sample_name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'lane': '2', 'description': '', 'sample_id': 'test-1705225-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A013', 'sample_well': 'E2', 'sample_project': '', 'library_nm': '80.66875653', 'sample_name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'lane': '2', 'description': '', 'sample_id': 'test-1705258-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A014', 'sample_well': 'F2', 'sample_project': '', 'library_nm': '61.96447231', 'sample_name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'lane': '2', 'description': '', 'sample_id': 'test-1705259-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A018', 'sample_well': 'G2', 'sample_project': '', 'library_nm': '86.20689655', 'sample_name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'lane': '2', 'description': '', 'sample_id': 'test-1705266-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A019', 'sample_well': 'H2', 'sample_project': '', 'library_nm': '54.44096134', 'sample_name': 'test-1705266-05'},
        {'index': 'ATCACG', 'lane': '2', 'description': '', 'sample_id': 'test-1705355-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A001', 'sample_well': 'A4', 'sample_project': '', 'library_nm': '80.77324974', 'sample_name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'lane': '2', 'description': '', 'sample_id': 'test-1705387-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A003', 'sample_well': 'B4', 'sample_project': '', 'library_nm': '81.19122257', 'sample_name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'lane': '2', 'description': '', 'sample_id': 'test-1705388-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A008', 'sample_well': 'C4', 'sample_project': '', 'library_nm': '79.41483804', 'sample_name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'lane': '2', 'description': '', 'sample_id': 'test-1705398-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A010', 'sample_well': 'D4', 'sample_project': '', 'library_nm': '66.24869383', 'sample_name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'lane': '2', 'description': '', 'sample_id': 'test-1705431-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A020', 'sample_well': 'E4', 'sample_project': '', 'library_nm': '74.08568443', 'sample_name': 'test-1705431-05'},
        {'index': 'CGTACG', 'lane': '2', 'description': '', 'sample_id': 'test-1705432-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A022', 'sample_well': 'F4', 'sample_project': '', 'library_nm': '79.83281087', 'sample_name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'lane': '2', 'description': '', 'sample_id': 'PCS-1724772-01', 'sample_type': 'Control', 'sample_plate': '', 'i7_index_id': 'A025', 'sample_well': 'G4', 'sample_project': '', 'library_nm': '76.07105538', 'sample_name': 'PCS-1724772-01'}
    ]

    samplesheet_lines_r = [ line for line in samplesheet.lines_r() ]
    assert samplesheet_lines_r == [
        {'index': 'CGATGT', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705166-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A002', 'Sample_Well': 'A2', 'Sample_Project': '', 'Library_nM': '69.07001045', 'Sample_Name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705169-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A005', 'Sample_Well': 'B2', 'Sample_Project': '', 'Library_nM': '62.27795193', 'Sample_Name': 'test-1705169-05'},
        {'index': 'CAGATC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705170-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A007', 'Sample_Well': 'C2', 'Sample_Project': '', 'Library_nM': '58.51619645', 'Sample_Name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705183-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A012', 'Sample_Well': 'D2', 'Sample_Project': '', 'Library_nM': '49.11180773', 'Sample_Name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705225-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A013', 'Sample_Well': 'E2', 'Sample_Project': '', 'Library_nM': '80.66875653', 'Sample_Name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705258-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A014', 'Sample_Well': 'F2', 'Sample_Project': '', 'Library_nM': '61.96447231', 'Sample_Name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705259-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A018', 'Sample_Well': 'G2', 'Sample_Project': '', 'Library_nM': '86.20689655', 'Sample_Name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705266-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A019', 'Sample_Well': 'H2', 'Sample_Project': '', 'Library_nM': '54.44096134', 'Sample_Name': 'test-1705266-05'},
        {'index': 'ATCACG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705355-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A001', 'Sample_Well': 'A4', 'Sample_Project': '', 'Library_nM': '80.77324974', 'Sample_Name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705387-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A003', 'Sample_Well': 'B4', 'Sample_Project': '', 'Library_nM': '81.19122257', 'Sample_Name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705388-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A008', 'Sample_Well': 'C4', 'Sample_Project': '', 'Library_nM': '79.41483804', 'Sample_Name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705398-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A010', 'Sample_Well': 'D4', 'Sample_Project': '', 'Library_nM': '66.24869383', 'Sample_Name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705431-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A020', 'Sample_Well': 'E4', 'Sample_Project': '', 'Library_nM': '74.08568443', 'Sample_Name': 'test-1705431-05'},
        {'index': 'CGTACG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705432-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A022', 'Sample_Well': 'F4', 'Sample_Project': '', 'Library_nM': '79.83281087', 'Sample_Name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'Lane': '1', 'Description': '', 'Sample_ID': 'PCS-1724772-01', 'SampleType': 'Control', 'Sample_Plate': '', 'I7_Index_ID': 'A025', 'Sample_Well': 'G4', 'Sample_Project': '', 'Library_nM': '76.07105538', 'Sample_Name': 'PCS-1724772-01'},
        {'index': 'CGATGT', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705166-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A002', 'Sample_Well': 'A2', 'Sample_Project': '', 'Library_nM': '69.07001045', 'Sample_Name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705169-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A005', 'Sample_Well': 'B2', 'Sample_Project': '', 'Library_nM': '62.27795193', 'Sample_Name': 'test-1705169-05'},
        {'index': 'CAGATC', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705170-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A007', 'Sample_Well': 'C2', 'Sample_Project': '', 'Library_nM': '58.51619645', 'Sample_Name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705183-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A012', 'Sample_Well': 'D2', 'Sample_Project': '', 'Library_nM': '49.11180773', 'Sample_Name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705225-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A013', 'Sample_Well': 'E2', 'Sample_Project': '', 'Library_nM': '80.66875653', 'Sample_Name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705258-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A014', 'Sample_Well': 'F2', 'Sample_Project': '', 'Library_nM': '61.96447231', 'Sample_Name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705259-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A018', 'Sample_Well': 'G2', 'Sample_Project': '', 'Library_nM': '86.20689655', 'Sample_Name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705266-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A019', 'Sample_Well': 'H2', 'Sample_Project': '', 'Library_nM': '54.44096134', 'Sample_Name': 'test-1705266-05'},
        {'index': 'ATCACG', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705355-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A001', 'Sample_Well': 'A4', 'Sample_Project': '', 'Library_nM': '80.77324974', 'Sample_Name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705387-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A003', 'Sample_Well': 'B4', 'Sample_Project': '', 'Library_nM': '81.19122257', 'Sample_Name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705388-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A008', 'Sample_Well': 'C4', 'Sample_Project': '', 'Library_nM': '79.41483804', 'Sample_Name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705398-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A010', 'Sample_Well': 'D4', 'Sample_Project': '', 'Library_nM': '66.24869383', 'Sample_Name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705431-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A020', 'Sample_Well': 'E4', 'Sample_Project': '', 'Library_nM': '74.08568443', 'Sample_Name': 'test-1705431-05'},
        {'index': 'CGTACG', 'Lane': '2', 'Description': '', 'Sample_ID': 'test-1705432-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A022', 'Sample_Well': 'F4', 'Sample_Project': '', 'Library_nM': '79.83281087', 'Sample_Name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'Lane': '2', 'Description': '', 'Sample_ID': 'PCS-1724772-01', 'SampleType': 'Control', 'Sample_Plate': '', 'I7_Index_ID': 'A025', 'Sample_Well': 'G4', 'Sample_Project': '', 'Library_nM': '76.07105538', 'Sample_Name': 'PCS-1724772-01'}
    ]

    assert samplesheet.validate() == True

    massaged_samplesheet = samplesheet.massage()
    assert massaged_samplesheet.split('\n')[2] == 'Investigator Name,9999999_666666_HFNC5BCXY,,,,,,,,,'

    assert samplesheet.to_demux() == """FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
HFNC5BCXY,1,test-1705166-05,hg19,CGATGT,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705169-05,hg19,ACAGTG,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705170-05,hg19,CAGATC,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705183-06,hg19,CTTGTA,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705225-05,hg19,AGTCAA,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705258-05,hg19,AGTTCC,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705259-05,hg19,GTCCGC,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705266-05,hg19,GTGAAA,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705355-05,hg19,ATCACG,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705387-05,hg19,TTAGGC,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705388-05,hg19,ACTTGA,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705398-06,hg19,TAGCTT,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705431-05,hg19,GTGGCC,Test,666666,R1,NN,666666
HFNC5BCXY,1,test-1705432-05,hg19,CGTACG,Test,666666,R1,NN,666666
HFNC5BCXY,1,PCS-1724772-01,hg19,ACTGAT,Control,666666,R1,NN,666666
HFNC5BCXY,2,test-1705166-05,hg19,CGATGT,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705169-05,hg19,ACAGTG,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705170-05,hg19,CAGATC,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705183-06,hg19,CTTGTA,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705225-05,hg19,AGTCAA,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705258-05,hg19,AGTTCC,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705259-05,hg19,GTCCGC,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705266-05,hg19,GTGAAA,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705355-05,hg19,ATCACG,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705387-05,hg19,TTAGGC,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705388-05,hg19,ACTTGA,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705398-06,hg19,TAGCTT,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705431-05,hg19,GTGGCC,Test,666666,R1,NN,666666
HFNC5BCXY,2,test-1705432-05,hg19,CGTACG,Test,666666,R1,NN,666666
HFNC5BCXY,2,PCS-1724772-01,hg19,ACTGAT,Control,666666,R1,NN,666666"""

    expected_samples = ['test-1705166-05', 'test-1705169-05', 'test-1705170-05', 'test-1705183-06', 'test-1705225-05', 'test-1705258-05', 'test-1705259-05', 'test-1705266-05', 'test-1705355-05', 'test-1705387-05', 'test-1705388-05', 'test-1705398-06', 'test-1705431-05', 'test-1705432-05', 'PCS-1724772-01', 'test-1705166-05', 'test-1705169-05', 'test-1705170-05', 'test-1705183-06', 'test-1705225-05', 'test-1705258-05', 'test-1705259-05', 'test-1705266-05', 'test-1705355-05', 'test-1705387-05', 'test-1705388-05', 'test-1705398-06', 'test-1705431-05', 'test-1705432-05', 'PCS-1724772-01']
    samples = [ sample for sample in samplesheet.samples() ]
    samples_r = [ sample for sample in samplesheet.samples_r(column='Sample_ID') ]
    assert samples == expected_samples
    assert samples_r == expected_samples

    assert samplesheet.is_pooled_lane('1') == True
    assert samplesheet.is_pooled_lane('2') == True
    assert samplesheet.is_pooled_lane_r('1', column='Lane') == True
    assert samplesheet.is_pooled_lane_r('2', column='Lane') == True

    expectes_lines = [
        {'index': 'CGATGT', 'lane': '1', 'description': '', 'sample_id': 'test-1705166-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A002', 'sample_well': 'A2', 'sample_project': '', 'library_nm': '69.07001045', 'sample_name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'lane': '1', 'description': '', 'sample_id': 'test-1705169-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A005', 'sample_well': 'B2', 'sample_project': '', 'library_nm': '62.27795193', 'sample_name': 'test-1705169-05'},
        {'index': 'CAGATC', 'lane': '1', 'description': '', 'sample_id': 'test-1705170-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A007', 'sample_well': 'C2', 'sample_project': '', 'library_nm': '58.51619645', 'sample_name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'lane': '1', 'description': '', 'sample_id': 'test-1705183-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A012', 'sample_well': 'D2', 'sample_project': '', 'library_nm': '49.11180773', 'sample_name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'lane': '1', 'description': '', 'sample_id': 'test-1705225-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A013', 'sample_well': 'E2', 'sample_project': '', 'library_nm': '80.66875653', 'sample_name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'lane': '1', 'description': '', 'sample_id': 'test-1705258-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A014', 'sample_well': 'F2', 'sample_project': '', 'library_nm': '61.96447231', 'sample_name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'lane': '1', 'description': '', 'sample_id': 'test-1705259-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A018', 'sample_well': 'G2', 'sample_project': '', 'library_nm': '86.20689655', 'sample_name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'lane': '1', 'description': '', 'sample_id': 'test-1705266-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A019', 'sample_well': 'H2', 'sample_project': '', 'library_nm': '54.44096134', 'sample_name': 'test-1705266-05'},
        {'index': 'ATCACG', 'lane': '1', 'description': '', 'sample_id': 'test-1705355-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A001', 'sample_well': 'A4', 'sample_project': '', 'library_nm': '80.77324974', 'sample_name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'lane': '1', 'description': '', 'sample_id': 'test-1705387-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A003', 'sample_well': 'B4', 'sample_project': '', 'library_nm': '81.19122257', 'sample_name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'lane': '1', 'description': '', 'sample_id': 'test-1705388-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A008', 'sample_well': 'C4', 'sample_project': '', 'library_nm': '79.41483804', 'sample_name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'lane': '1', 'description': '', 'sample_id': 'test-1705398-06', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A010', 'sample_well': 'D4', 'sample_project': '', 'library_nm': '66.24869383', 'sample_name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'lane': '1', 'description': '', 'sample_id': 'test-1705431-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A020', 'sample_well': 'E4', 'sample_project': '', 'library_nm': '74.08568443', 'sample_name': 'test-1705431-05'},
        {'index': 'CGTACG', 'lane': '1', 'description': '', 'sample_id': 'test-1705432-05', 'sample_type': 'Test', 'sample_plate': '', 'i7_index_id': 'A022', 'sample_well': 'F4', 'sample_project': '', 'library_nm': '79.83281087', 'sample_name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'lane': '1', 'description': '', 'sample_id': 'PCS-1724772-01', 'sample_type': 'Control', 'sample_plate': '', 'i7_index_id': 'A025', 'sample_well': 'G4', 'sample_project': '', 'library_nm': '76.07105538', 'sample_name': 'PCS-1724772-01'}
    ]
    lines = [ line for line in samplesheet.lines_per_column('lane', '1') ]
    assert lines == expectes_lines

    expectes_lines_r = [
        {'index': 'CGATGT', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705166-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A002', 'Sample_Well': 'A2', 'Sample_Project': '', 'Library_nM': '69.07001045', 'Sample_Name': 'test-1705166-05'},
        {'index': 'ACAGTG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705169-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A005', 'Sample_Well': 'B2', 'Sample_Project': '', 'Library_nM': '62.27795193', 'Sample_Name': 'test-1705169-05'},
        {'index': 'CAGATC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705170-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A007', 'Sample_Well': 'C2', 'Sample_Project': '', 'Library_nM': '58.51619645', 'Sample_Name': 'test-1705170-05'},
        {'index': 'CTTGTA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705183-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A012', 'Sample_Well': 'D2', 'Sample_Project': '', 'Library_nM': '49.11180773', 'Sample_Name': 'test-1705183-06'},
        {'index': 'AGTCAA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705225-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A013', 'Sample_Well': 'E2', 'Sample_Project': '', 'Library_nM': '80.66875653', 'Sample_Name': 'test-1705225-05'},
        {'index': 'AGTTCC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705258-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A014', 'Sample_Well': 'F2', 'Sample_Project': '', 'Library_nM': '61.96447231', 'Sample_Name': 'test-1705258-05'},
        {'index': 'GTCCGC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705259-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A018', 'Sample_Well': 'G2', 'Sample_Project': '', 'Library_nM': '86.20689655', 'Sample_Name': 'test-1705259-05'},
        {'index': 'GTGAAA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705266-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A019', 'Sample_Well': 'H2', 'Sample_Project': '', 'Library_nM': '54.44096134', 'Sample_Name': 'test-1705266-05'},
        {'index': 'ATCACG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705355-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A001', 'Sample_Well': 'A4', 'Sample_Project': '', 'Library_nM': '80.77324974', 'Sample_Name': 'test-1705355-05'},
        {'index': 'TTAGGC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705387-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A003', 'Sample_Well': 'B4', 'Sample_Project': '', 'Library_nM': '81.19122257', 'Sample_Name': 'test-1705387-05'},
        {'index': 'ACTTGA', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705388-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A008', 'Sample_Well': 'C4', 'Sample_Project': '', 'Library_nM': '79.41483804', 'Sample_Name': 'test-1705388-05'},
        {'index': 'TAGCTT', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705398-06', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A010', 'Sample_Well': 'D4', 'Sample_Project': '', 'Library_nM': '66.24869383', 'Sample_Name': 'test-1705398-06'},
        {'index': 'GTGGCC', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705431-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A020', 'Sample_Well': 'E4', 'Sample_Project': '', 'Library_nM': '74.08568443', 'Sample_Name': 'test-1705431-05'},
        {'index': 'CGTACG', 'Lane': '1', 'Description': '', 'Sample_ID': 'test-1705432-05', 'SampleType': 'Test', 'Sample_Plate': '', 'I7_Index_ID': 'A022', 'Sample_Well': 'F4', 'Sample_Project': '', 'Library_nM': '79.83281087', 'Sample_Name': 'test-1705432-05'},
        {'index': 'ACTGAT', 'Lane': '1', 'Description': '', 'Sample_ID': 'PCS-1724772-01', 'SampleType': 'Control', 'Sample_Plate': '', 'I7_Index_ID': 'A025', 'Sample_Well': 'G4', 'Sample_Project': '', 'Library_nM': '76.07105538', 'Sample_Name': 'PCS-1724772-01'}
    ]
    lines_r = [ line for line in samplesheet.lines_per_column_r('Lane', '1') ]
    assert lines_r == expectes_lines_r


def test_x_samplesheet():
    samplesheet = Samplesheet('tests/fixtures/x_samplesheet.csv')

    assert samplesheet.raw() == """[Data]
FCID,Lane,SampleID,SampleRef,index,SampleName,Control,Recipe,Operator,Project
HC7H2ALXX,1,SVE2274A2_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262
HC7H2ALXX,2,SVE2274A4_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262
HC7H2ALXX,3,SVE2274A6_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262
HC7H2ALXX,4,SVE2274A7_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262
HC7H2ALXX,5,SVE2274A8_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262
HC7H2ALXX,6,SVE2274A9_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262
HC7H2ALXX,7,SVE2274A10_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262
HC7H2ALXX,8,SVE2274A11_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262"""


    samplesheet_lines = [ line for line in samplesheet.lines() ]
    assert samplesheet_lines == [
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '1', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A2_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '2', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A4_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '3', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A6_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '4', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A7_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '5', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A8_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '6', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A9_TCTCGCGC', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCTCGCGC'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '7', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A10_TCTCGCGC', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCTCGCGC'},
        {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '8', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A11_TCTCGCGC', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCTCGCGC'}
    ]

    samplesheet_lines_r = [ line for line in samplesheet.lines_r() ]
    assert samplesheet_lines_r == [
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '1', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A2_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '2', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A4_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '3', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A6_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '4', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A7_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '5', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A8_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '6', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A9_TCTCGCGC', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCTCGCGC'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '7', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A10_TCTCGCGC', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCTCGCGC'},
        {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '8', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A11_TCTCGCGC', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCTCGCGC'}
    ]

    assert samplesheet.validate() == True

    expected_samples = [ 'SVE2274A2_TCCGCGAA', 'SVE2274A4_TCCGCGAA', 'SVE2274A6_TCCGCGAA',
                          'SVE2274A7_TCCGCGAA', 'SVE2274A8_TCCGCGAA', 'SVE2274A9_TCTCGCGC',
                          'SVE2274A10_TCTCGCGC', 'SVE2274A11_TCTCGCGC']
    samples = [ sample for sample in samplesheet.samples() ]
    samples_r = [ sample for sample in samplesheet.samples_r() ]
    assert samples == expected_samples
    assert samples_r == expected_samples

    assert samplesheet.is_pooled_lane(1) == False
    assert samplesheet.is_pooled_lane(2) == False
    assert samplesheet.is_pooled_lane(3) == False
    assert samplesheet.is_pooled_lane(4) == False
    assert samplesheet.is_pooled_lane(5) == False
    assert samplesheet.is_pooled_lane(6) == False
    assert samplesheet.is_pooled_lane(7) == False
    assert samplesheet.is_pooled_lane(8) == False

    assert samplesheet.is_pooled_lane_r(1, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(2, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(3, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(4, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(5, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(6, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(7, column='Lane') == False
    assert samplesheet.is_pooled_lane_r(8, column='Lane') == False

    expected_lines = [ {'control': 'N', 'fcid': 'HC7H2ALXX', 'lane': '1', 'operator': 'NN', 'project': '659262', 'recipe': 'R1', 'sample_id': 'SVE2274A2_TCCGCGAA', 'sample_name': '659262', 'sample_ref': 'hg19', 'index': 'TCCGCGAA'} ]
    lines = [ line for line in samplesheet.lines_per_column('lane', '1') ]
    assert lines == expected_lines

    lines_r = [ line for line in samplesheet.lines_per_column_r('Lane', '1') ]
    expected_lines = [ {'Control': 'N', 'FCID': 'HC7H2ALXX', 'Lane': '1', 'Operator': 'NN', 'Project': '659262', 'Recipe': 'R1', 'SampleID': 'SVE2274A2_TCCGCGAA', 'SampleName': '659262', 'SampleRef': 'hg19', 'index': 'TCCGCGAA'} ]
    assert lines_r == expected_lines

    expected_lanes = ['1', '2', '3', '4', '5', '6', '7', '8']
    lanes = [ lane for lane in samplesheet.column('lane') ]
    lanes_r = [ lane for lane in samplesheet.column_r('Lane') ]
    assert lanes == expected_lanes
    assert lanes_r == expected_lanes

    lines = list(samplesheet.lines())
    assert lines[0].dualindex == 'TCCGCGAA'


def test_x_faulty_samplesheet():
    samplesheet = Samplesheet('tests/fixtures/x_faulty_samplesheet.csv')

    with pytest.raises(SampleSheetValidationException):
        samplesheet.validate()

def test_2500_faulty_samplesheet():
    samplesheet = HiSeq2500Samplesheet('tests/fixtures/2500_faulty_samplesheet.csv')

    with pytest.raises(SampleSheetValidationException):
        samplesheet.validate()

def test_2500_samplesheet():
    samplesheet = HiSeq2500Samplesheet('tests/fixtures/2500_samplesheet.csv')

    assert samplesheet.raw() == """FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
HB07NADXX,1,SIB911A1_sureselect4,hg19,TGACCA,959191,N,R1,NN,959191
HB07NADXX,1,SIB911A2_sureselect5,hg19,ACAGTG,959191,N,R1,NN,959191
HB07NADXX,1,SIB910A3_sureselect6,hg19,GCCAAT,454557,N,R1,NN,454557
HB07NADXX,1,SIB914A2_sureselect2,hg19,CGATGT,504910,N,R1,NN,504910
HB07NADXX,1,SIB914A11_sureselect11,hg19,GGCTAC,504910,N,R1,NN,504910
HB07NADXX,1,SIB914A12_sureselect12,hg19,CTTGTA,504910,N,R1,NN,504910
HB07NADXX,1,SIB914A15_sureselect15,hg19,GAAACC,504910,N,R1,NN,504910
HB07NADXX,2,SIB911A1_sureselect4,hg19,TGACCA,959191,N,R1,NN,959191
HB07NADXX,2,SIB911A2_sureselect5,hg19,ACAGTG,959191,N,R1,NN,959191
HB07NADXX,2,SIB910A3_sureselect6,hg19,GCCAAT,454557,N,R1,NN,454557
HB07NADXX,2,SIB914A2_sureselect2,hg19,CGATGT,504910,N,R1,NN,504910
HB07NADXX,2,SIB914A11_sureselect11,hg19,GGCTAC,504910,N,R1,NN,504910
HB07NADXX,2,SIB914A12_sureselect12,hg19,CTTGTA,504910,N,R1,NN,504910
HB07NADXX,2,SIB914A15_sureselect15,hg19,GAAACC,504910,N,R1,NN,504910"""

    samplesheet_lines = [ line for line in samplesheet.lines() ]
    assert samplesheet_lines == [
        {'control': 'N', 'description': '959191', 'fcid': 'HB07NADXX', 'index': 'TGACCA', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB911A1_sureselect4', 'project': '959191', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '959191', 'fcid': 'HB07NADXX', 'index': 'ACAGTG', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB911A2_sureselect5', 'project': '959191', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '454557', 'fcid': 'HB07NADXX', 'index': 'GCCAAT', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB910A3_sureselect6', 'project': '454557', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'CGATGT', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A2_sureselect2', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'GGCTAC', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A11_sureselect11', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'CTTGTA', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A12_sureselect12', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'GAAACC', 'lane': '1', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A15_sureselect15', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '959191', 'fcid': 'HB07NADXX', 'index': 'TGACCA', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB911A1_sureselect4', 'project': '959191', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '959191', 'fcid': 'HB07NADXX', 'index': 'ACAGTG', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB911A2_sureselect5', 'project': '959191', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '454557', 'fcid': 'HB07NADXX', 'index': 'GCCAAT', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB910A3_sureselect6', 'project': '454557', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'CGATGT', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A2_sureselect2', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'GGCTAC', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A11_sureselect11', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'CTTGTA', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A12_sureselect12', 'project': '504910', 'sample_ref': 'hg19'},
        {'control': 'N', 'description': '504910', 'fcid': 'HB07NADXX', 'index': 'GAAACC', 'lane': '2', 'operator': 'NN', 'recipe': 'R1', 'sample_id': 'SIB914A15_sureselect15', 'project': '504910', 'sample_ref': 'hg19'}
    ]

    samplesheet_lines_r = [ line for line in samplesheet.lines_r() ]
    assert samplesheet_lines_r == [
        {'Control': 'N', 'Description': '959191', 'FCID': 'HB07NADXX', 'Index': 'TGACCA', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB911A1_sureselect4', 'SampleProject': '959191', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '959191', 'FCID': 'HB07NADXX', 'Index': 'ACAGTG', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB911A2_sureselect5', 'SampleProject': '959191', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '454557', 'FCID': 'HB07NADXX', 'Index': 'GCCAAT', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB910A3_sureselect6', 'SampleProject': '454557', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'CGATGT', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A2_sureselect2', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'GGCTAC', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A11_sureselect11', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'CTTGTA', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A12_sureselect12', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'GAAACC', 'Lane': '1', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A15_sureselect15', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '959191', 'FCID': 'HB07NADXX', 'Index': 'TGACCA', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB911A1_sureselect4', 'SampleProject': '959191', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '959191', 'FCID': 'HB07NADXX', 'Index': 'ACAGTG', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB911A2_sureselect5', 'SampleProject': '959191', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '454557', 'FCID': 'HB07NADXX', 'Index': 'GCCAAT', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB910A3_sureselect6', 'SampleProject': '454557', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'CGATGT', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A2_sureselect2', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'GGCTAC', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A11_sureselect11', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'CTTGTA', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A12_sureselect12', 'SampleProject': '504910', 'SampleRef': 'hg19'},
        {'Control': 'N', 'Description': '504910', 'FCID': 'HB07NADXX', 'Index': 'GAAACC', 'Lane': '2', 'Operator': 'NN', 'Recipe': 'R1', 'SampleID': 'SIB914A15_sureselect15', 'SampleProject': '504910', 'SampleRef': 'hg19'}
    ]

    assert samplesheet.validate() == True

    expected_samples = [ 'SIB911A1_sureselect4', 'SIB911A2_sureselect5', 'SIB910A3_sureselect6',
                         'SIB914A2_sureselect2', 'SIB914A11_sureselect11', 'SIB914A12_sureselect12',
                         'SIB914A15_sureselect15', 'SIB911A1_sureselect4', 'SIB911A2_sureselect5',
                         'SIB910A3_sureselect6', 'SIB914A2_sureselect2', 'SIB914A11_sureselect11',
                         'SIB914A12_sureselect12', 'SIB914A15_sureselect15' ]
    samples = [ sample for sample in samplesheet.samples() ]
    samples_r = [ sample for sample in samplesheet.samples_r() ]
    assert samples == expected_samples
    assert samples_r == expected_samples

    assert samplesheet.is_pooled_lane(1) == True
    assert samplesheet.is_pooled_lane(2) == True

    assert samplesheet.is_pooled_lane_r(1, column='Lane') == True
    assert samplesheet.is_pooled_lane_r(2, column='Lane') == True

    expected_lanes = ['1', '1', '1', '1', '1', '1', '1', '2', '2', '2', '2', '2', '2', '2']
    lanes = [ lane for lane in samplesheet.column('lane') ]
    lanes_r = [ lane for lane in samplesheet.column_r('Lane') ]
    assert lanes == expected_lanes
    assert lanes_r == expected_lanes


def test_miseq_samplesheet():
    samplesheet = MiseqSamplesheet('tests/fixtures/161129_M03284_0041_000000000-AY7H3/SampleSheet.csv')

    assert samplesheet._get_flowcell() == '000000000-AY7H3'

    with open('tests/fixtures/161129_M03284_0041_000000000-AY7H3/demux_samplesheet.csv') as demux_samplesheet:
        assert samplesheet.to_demux() == ''.join(demux_samplesheet.readlines()).rstrip('\n')
