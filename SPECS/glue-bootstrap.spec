%define _prefix /usr/glue

Name:           glue-bootstrap
Version:        1
Release:        1%{?dist}
Summary:        System bootstrap tools for Glue systems
License:	None
URL:            https://github.com/MrStaticVoid/glue-bootstrap
Source0:        https://github.com/MrStaticVoid/glue-bootstrap/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:	systemd
Requires:       puppet-agent
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description
Script and service that checks that the Puppet SSL keypair exists and
creates it if it doesn't.

%prep
%setup -qn %{name}-%{version}

%build
./autogen.sh
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%make_install

%post
%systemd_post glue-bootstrap.service

%preun
%systemd_preun glue-bootstrap.service

%postun
%systemd_postun

%files
%{_sbindir}/*
%{_unitdir}/*
