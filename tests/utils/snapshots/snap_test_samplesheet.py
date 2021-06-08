# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots[
    "test_convert_2500_samplesheet 1"
] = """[Data]
FCID,Lane,SampleID,SampleRef,index,index2,SampleName,Control,Recipe,Operator,Project
HFLOWCELL,1,Sample1,hg19,AAACAT,,630939,N,R1,NN,630939
HFLOWCELL,1,Sample2,hg19,ATCACG,,630939,N,R1,NN,630939
HFLOWCELL,1,Sample3,hg19,TTAGGC,,630939,N,R1,NN,630939
HFLOWCELL,1,Sample4,hg19,TGACCA,,630939,N,R1,NN,630939
HFLOWCELL,1,Sample5,hg19,ACAGTG,,630939,N,R1,NN,630939
HFLOWCELL,2,Sample1,hg19,AAACAT,,630939,N,R1,NN,630939
HFLOWCELL,2,Sample2,hg19,ATCACG,,630939,N,R1,NN,630939
HFLOWCELL,2,Sample3,hg19,TTAGGC,,630939,N,R1,NN,630939
HFLOWCELL,2,Sample4,hg19,TGACCA,,630939,N,R1,NN,630939
HFLOWCELL,2,Sample5,hg19,ACAGTG,,630939,N,R1,NN,630939"""
