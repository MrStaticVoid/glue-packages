%define _prefix /usr/glue

# See https://fedoraproject.org/wiki/Packaging:SourceURL?rd=Packaging/SourceURL#Git_Hosting_Services
%define commit0 d834135f4e209f9f658a28cfd40e339170310c91
%define gittag0 v2

Name:           glue-bootstrap
Version:        2
Release:        1%{?dist}
Summary:        System bootstrap tools for Glue systems
License:	None
URL:            https://gitlab.umd.edu/it-platform/glue-bootstrap
Source0:        https://gitlab.umd.edu/it-platform/glue-bootstrap/repository/archive.tar.gz?ref=%{gittag0}#/%{name}-%{version}.tar.gz

BuildRequires:	systemd
Requires:       puppet-agent
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description
Script and service that checks that the Puppet SSL keypair exists and
creates it if it doesn't.

%prep
%setup -qn %{name}-%{gittag0}-%{commit0}

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
