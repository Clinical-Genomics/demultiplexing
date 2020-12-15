# demultiplexing
![Build Status - Github][gh-actions-badge]
[![Coverage Status][coveralls-image]][coveralls-url]
[![Code style: black][black-image]][black-url]

To keep scripts associated with execution of the Illumina demultiplexing pipeline

There are two parts to this package: a pure bash part and a python package.

## Bash

All workflow related scripts are written in `bash`. They will set up the right environment to allow for easy demulitplexing and moving data around between locations and servers.

* demux.bash: the main script demultiplexing Illumina HiSeq2500 data (bcl2fastq).
* *nipt.bash: scripts enabling NIPT data processing.
* hiseqx/x*.bash: scripts for demultiplexing Illumina HiSeqX data (bcl2fastq).

## NIPT

The NIPT scripts require a .niptrc file to be placed in the excuting user's `$HOME`. A template has been provided.

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

You can install `demultiplexing` via pip

````bash
pip install demux
```` 

or via poetry:
```
$ git clone https://github.com/Clinical-Genomics/demultiplexing && cd demultiplexing
poetry install
poetry run demux
```

You also need a YAML config file describing how to connect to the LIMS instance. It should contain information like this:

```yaml
---
host: https://genologics.mycompany.com
username: apiuser
password: somepassword
```

Files will be blacked automatically with each push to github. If you would like to automatically [Black][black-url] format your commits on your local machine:

```
pre-commit install
```

## Contributing

Please check out our [guide for contributing to demultiplexing](CONTRIBUTING.md)

[coveralls-url]: https://coveralls.io/github/Clinical-Genomics/demultiplexing
[black-url]: https://github.com/psf/black

<!-- badges -->
[gh-actions-badge]: https://github.com/Clinical-Genomics/demultiplexing/workflows/Demultiplexing%20CI/badge.svg
[coveralls-image]: https://coveralls.io/repos/github/Clinical-Genomics/demultiplexing/badge.svg?branch=master
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
