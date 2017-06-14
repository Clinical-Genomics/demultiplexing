# demultiplexing [![Build Status][travis-img]][travis-url]

To keep scripts associated with execution of the Illumina demultiplexing pipeline

There are two parts to this package: a pure bash part and a python package.

## Bash

All workflow related scripts are written in `bash`. They will set up the right environment to allow for easy demulitplexing and moving data around between locations and servers.

* demux.bash: the main script demultiplexing Illumina HiSeq2500 data (bcl2fastq).
* *nipt.bash: scripts enabling NIPT data processing.
* hiseqx/x*.bash: scripts for demultiplexing Illumina HiSeqX data (bcl2fastq).

## python

All SampleSheet related actions are bundled in a python package enabling easier testing.

```bash
$ demux sheet --help
Usage: demux sheet [OPTIONS] COMMAND [ARGS]...

  Samplesheet commands

Options:
  --help  Show this message and exit.

Commands:
  demux     Convert a machine samplesheet for demux
  fetch     Fetch a samplesheet from LIMS
  massage   create a NIPT ready SampleSheet
  validate  validate a samplesheet
```

## Installation

You can install `demultiplexing` from source:

```bash
$ git clone https://github.com/Clinical-Genomics/demultiplexing && cd demultiplexing
$ pip install --editable .
```

You also need a YAML config file describing how to connect to the LIMS instance. It should contain information like this:

```yaml
---
host: https://genologics.mycompany.com
username: apiuser
password: somepassword
```

[travis-img]: https://api.travis-ci.org/Clinical-Genomics/demultiplexing.svg?branch=master?style=flat-square
[travis-url]: https://travis-ci.org/Clinical-Genomics/demultiplexing
