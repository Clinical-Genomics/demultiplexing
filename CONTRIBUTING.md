# Contributing to Demultiplexing

## Versioning
Demultiplexing adheres to [semantic versioning].

## Branch Model

Demultiplexing is using github flow branching model as described in our [development manual][development-branch-model].

## Publishing

Bump the version according to semantic versioning locally on branch `master` using [bumpversion]:

```
bumpversion [major | minor | patch ]
```

Reinstall the application with the new version:

```
poetry install
```

Build and publish to PyPi:

```
poetry build
poetry publish
```

Push to git:
```
git push
git push --tag
```

This will trigger a new docker build using the git release tag as name.

[bumpversion]: https://github.com/c4urself/bump2version
[development-branch-model]: http://www.clinicalgenomics.se/development/dev/models/
[semantic versioning]: https://semver.org/