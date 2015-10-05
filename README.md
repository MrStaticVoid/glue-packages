# Glue Packages #

## Creating a new package ##

```
rpmdev-newspec SPECS/package-name.spec
```

## Building a package ##

```
./do spectool -R -g SPECS/package-name.spec
./do rpmbuild -bb --sign --define 'dist .el7' SPECS/package-name.spec
```
