%define _prefix /usr/glue

Name:           glue-scripts
Version:        1
Release:        1%{?dist}
Summary:        Miscellaneous scripts for Glue systems
License:	None
URL:            https://github.com/MrStaticVoid/glue-scripts
Source0:        https://github.com/MrStaticVoid/glue-scripts/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:	glue-scripts.sh.in
Source2:	glue-scripts.csh.in

Requires:       zsh

%description
Miscellaneous scripts for Glue systems

%prep
%setup -qn %{name}-%{version}
sed -e 's,[@]bindir[@],%{_bindir},g' %SOURCE1 > glue-scripts.sh
sed -e 's,[@]bindir[@],%{_bindir},g' %SOURCE2 > glue-scripts.csh

%build
./autogen.sh
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%make_install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
cp glue-scripts.sh $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/glue-scripts.sh
cp glue-scripts.csh $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/glue-scripts.csh

%files
%{_bindir}/*
%{_sysconfdir}/profile.d/*
