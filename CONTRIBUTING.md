# Contributing to Demultiplexing

## Versioning
Demultiplexing adheres to [semantic versioning].

## Branch Model

Demultiplexing is using github flow branching model as described in our [development manual][development-branch-model].

## Publishing to PyPi

Bump the version according to semantic versioning locally on branch `master` using poetry:

```
poetry version [major | minor | patch ]
```

Reinstall the application with the new version:

```
poetry install
```

Build and publish:

```
poetry build
poetry publish
```

[development-branch-model]: http://www.clinicalgenomics.se/development/dev/models/
[semantic versioning]: https://semver.org/