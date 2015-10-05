# Glue Packages #

## Creating a new package ##

```
rpmdev-newspec SPECS/package-name.spec
```

## Building a package ##

```
./do spectool -Rg SPECS/package-name.spec
./do rpmbuild -bb --sign SPECS/package-name.spec
```
