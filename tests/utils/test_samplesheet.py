#!/usr/bin/env python
# -*- coding: utf-8 -*-

from demux.utils import Samplesheet

def test_nipt_samplesheet():
    samplesheet = Samplesheet('tests/fixtures/nipt_samplesheet.csv')

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

    # ok, time to change the sample sheet a bit!
    samplesheet.massage()
    assert samplesheet.section[samplesheet.HEADER][2][1] == '9999999_666666_HFNC5BCXY'

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

    samples = [ sample for sample in samplesheet.samples('Sample_ID') ]
    assert samples == ['test-1705166-05', 'test-1705169-05', 'test-1705170-05', 'test-1705183-06', 'test-1705225-05', 'test-1705258-05', 'test-1705259-05', 'test-1705266-05', 'test-1705355-05', 'test-1705387-05', 'test-1705388-05', 'test-1705398-06', 'test-1705431-05', 'test-1705432-05', 'PCS-1724772-01', 'test-1705166-05', 'test-1705169-05', 'test-1705170-05', 'test-1705183-06', 'test-1705225-05', 'test-1705258-05', 'test-1705259-05', 'test-1705266-05', 'test-1705355-05', 'test-1705387-05', 'test-1705388-05', 'test-1705398-06', 'test-1705431-05', 'test-1705432-05', 'PCS-1724772-01']

    assert samplesheet.is_pooled_lane('1', column='Lane') == True
    assert samplesheet.is_pooled_lane('2', column='Lane') == True
