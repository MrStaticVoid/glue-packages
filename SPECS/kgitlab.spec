# See: http://fedoraproject.org/wiki/Packaging:Ruby#Applications
%global app_root %{_datadir}/%{name}

Name:           kgitlab
Version:        0.0.2
Release:        1%{?dist}
Summary:        Utilities for enabling Kerberos authentication for GitLab
License:	None
URL:            https://github.com/MrStaticVoid/kgitlab
Source0:        https://github.com/MrStaticVoid/kgitlab/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:	ruby
BuildRequires:	ruby-devel
BuildRequires:	rubygem-bundler
BuildRequires:	systemd
Requires:	ruby
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description
A GitLab system hook listener and associated tools for automatically
managing the git user's .k5login file

%prep
%setup -qn %{name}-%{version}
sed -e 's,[@]bindir[@],%{_bindir},g; s,[@]sysconfdir[@],%{_sysconfdir},g' kgitlab.service.in > kgitlab.service

%build

%install
mkdir -p %{buildroot}%{app_root}
bundle install --path %{buildroot}%{app_root}
bundle exec rake install

mkdir -p %{buildroot}%{_unitdir}
cp kgitlab.service %{buildroot}%{_unitdir}/kgitlab.service

mkdir -p %{buildroot}%{_sysconfdir}/kgitlab
cp config.yaml.example %{buildroot}%{_sysconfdir}/kgitlab/config.yaml

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/kgitlab <<END
#!/usr/bin/ruby
ENV['GEM_PATH'] = '%{app_root}/ruby'
Gem.clear_paths 
load '%{app_root}/ruby/bin/kgitlab'
END
chmod +x %{buildroot}%{_bindir}/kgitlab

cat > %{buildroot}%{_bindir}/kgitlabsh <<END
#!/bin/bash
exec /usr/bin/kgitlab exec-shell "\$@"
END
chmod +x %{buildroot}%{_bindir}/kgitlabsh

# gem hardcodes buildroot into binary libraries
# http://adam.younglogic.com/2010/05/found-buildroot-in-installed-files-aborting/
find $RPM_BUILD_ROOT -type f -exec sed -i "s@$RPM_BUILD_ROOT@@g" {} \;

%post
%systemd_post kgitlab.service

%preun
%systemd_preun kgitlab.service

%postun
%systemd_postun_with_restart kgitlab.service

%files
%config %attr(600, root, root) %{_sysconfdir}/kgitlab/config.yaml
%{_bindir}/kgitlab
%{_bindir}/kgitlabsh
%{_unitdir}/kgitlab.service
%{app_root}/*
