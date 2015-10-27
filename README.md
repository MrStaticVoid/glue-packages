#### Table of Contents

1. [Creating a new package](#creating-a-new-package)
2. [Installing build dependencies](#installing-build-dependencies)
3. [Building a package](#building-a-package)

## Creating a new package

`rpmdevtools` provides a number of boilerplate spec files to get started from.  See the output of `rpmdev-newspec --help` to see the list of package types it can generate specs for.  At a minimum, you can use

```
$ rpmdev-newspec SPECS/package-name.spec
```

to get started, or copy and modify an existing spec file, like `glue-bootstrap.spec` or `glue-scripts.spec`.

The benefit of using spec files to build packages is [tons of documentation](https://fedoraproject.org/wiki/How_to_create_an_RPM_package), [a fairly good set of standards to start from](https://fedoraproject.org/wiki/Packaging:Guidelines), and plenty of good macros to make our lives easier.

## Installing build dependencies

Pull in any build dependencies specified by the spec file:

```
# yum-builddeps SPECS/package-name.spec
```

## Building a package

The following two commands will download package source files (if URLs to the source are provided in the spec file) and then build and sign the package file.

```
$ ./do spectool -R -g SPECS/package-name.spec
$ ./do rpmbuild -bb --sign --define 'dist .el7' SPECS/package-name.spec
```

You will have to run the `do rpmbuild` command with AFS admin rights to be able to read the GPG key.
