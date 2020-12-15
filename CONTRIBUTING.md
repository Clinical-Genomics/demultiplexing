# Contributing to Demultiplexing

## Versioning
Demultiplexing adheres to [semantic versioning].

## Branch Model

Demultiplexing is using github flow branching model as described in our [development manual][development-branch-model].

## Publishing to PyPi

Bump the version according to semantic versioning locally on branch `master` using [bumpversion]:

```
bumpversion [major | minor | patch ]
git push
git push --tag
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

[bumpversion]: https://github.com/c4urself/bump2version
[development-branch-model]: http://www.clinicalgenomics.se/development/dev/models/
[semantic versioning]: https://semver.org/