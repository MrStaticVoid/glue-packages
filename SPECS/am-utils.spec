Summary: Automount utilities including an updated version of Amd
Name: am-utils
Version: 6.2
Release: 1%{?dist}
License: BSD
Epoch: 5
Group: System Environment/Daemons
URL: http://am-utils.org
Source: ftp://ftp.am-utils.org/pub/am-utils/am-utils-%{version}.tar.gz
Source1: amd.service
Source2: am-utils.conf
Source3: am-utils.sysconf
Source4: am-utils.net.map

BuildRequires: gdbm-devel
BuildRequires: hesiod-devel
BuildRequires: openldap-devel
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: bison
BuildRequires: flex
BuildRequires: tcp_wrappers-devel
BuildRequires: systemd-units
BuildRequires: texinfo
BuildRequires: gcc
BuildRequires: m4

Requires: portmap
Requires: grep
Requires: gawk
Requires: findutils

Requires(pre):    /bin/grep
Requires(post):   /sbin/install-info
Requires(post):   systemd-sysv
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(preun):  /sbin/install-info

# Not needed since autoreconf/libtool appear to do this automatically
# Leaving it set doesn't appear to be a problem so leave it set in
# case this changes.
%global _hardened_build 1

# We need to filter out some perl requirements for now.
%define _use_internal_dependency_generator 0
%define old_find_requires %{__find_requires}

%description
Am-utils includes an updated version of Amd, the popular BSD
automounter.  An automounter is a program which maintains a cache
of mounted filesystems.  Filesystems are mounted when they are
first referenced by the user and unmounted after a certain period of
inactivity. Amd supports a variety of filesystems, including NFS, UFS,
CD-ROMS and local drives.

You should install am-utils if you need a program for automatically
mounting and unmounting filesystems.

%prep
%setup -q -n %{name}-%{version}

./bootstrap

find_requires=%{old_find_requires}
echo "$find_requires | grep -v lostaltmail.conf" > find-requires
chmod +x find-requires

%build
%configure \
        --enable-shared \
        --enable-am-cflags="-DHAVE_LINUX_NFS_MOUNT_H" \
        --enable-libs="-lnsl -lresolv"

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_flags}

%install
%makeinstall

mkdir -p ${RPM_BUILD_ROOT}/%{_sysconfdir}/sysconfig
mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}

install -m 755 %{SOURCE1} ${RPM_BUILD_ROOT}/%{_unitdir}/
install -m 600 %{SOURCE2} ${RPM_BUILD_ROOT}/%{_sysconfdir}/amd.conf
install -m 644 %{SOURCE3} ${RPM_BUILD_ROOT}/%{_sysconfdir}/sysconfig/amd
install -m 640 %{SOURCE4} ${RPM_BUILD_ROOT}/%{_sysconfdir}/amd.net

gzip -q9f ${RPM_BUILD_ROOT}/%{_infodir}/*info*
mkdir -p ${RPM_BUILD_ROOT}/.automount

rm -f ${RPM_BUILD_ROOT}/usr/sbin/ctl-amd

# add symlinks to shared libs
/sbin/ldconfig -n ${RPM_BUILD_ROOT}/%{_libdir}

# deprecated files
for I in %{_libdir}/libamu.a \
         %{_libdir}/libamu.la \
         %{_libdir}/libamu.so \
         %{_infodir}/dir \
         %{_sysconfdir}/amd.conf-sample \
         %{_sysconfdir}/lostaltmail.conf-sample; do

         rm -f  $RPM_BUILD_ROOT$I
done

%define __find_requires %{_builddir}/%{name}-%{version}/find-requires

%pre
# Check if we have an old fashioned amd.conf and rename if to amd.net
if test "$1" -ne 0; then
  if test -r /etc/amd.conf; then
    if grep -v -q "auto_dir" /etc/amd.conf; then
       if test ! -e /etc/amd.net; then
         mv -f /etc/amd.conf /etc/amd.net
       fi
    fi
  fi
fi

%post
/sbin/ldconfig
%systemd_post amd.service

if [ -f %{_infodir}/am-utils.info.gz ]; then
    /sbin/install-info %{_infodir}/am-utils.info.gz %{_infodir}/dir || :
fi

%preun
%systemd_preun amd.service

if [ $1 -eq 0 ]; then
   # Package removal, not upgrade
   if [ -f %{_infodir}/am-utils.info.gz ]; then
      /sbin/install-info --delete %{_infodir}/am-utils.info.gz %{_infodir}/dir || :
   fi
fi

%postun
%systemd_postun_with_restart amd.service

/sbin/ldconfig

%triggerun -- am-utils < 6.1.5-19
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply amd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save amd >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del amd >/dev/null 2>&1 || :
/bin/systemctl try-restart amd.service >/dev/null 2>&1 || :

%files
%doc doc/*.ps AUTHORS BUGS ChangeLog NEWS README* scripts/*-sample
%dir /.automount
%{_bindir}/pawd
%{_sbindir}/*
%{_mandir}/man[58]/*
%{_mandir}/man1/pawd.1*
%config(noreplace) %{_sysconfdir}/amd.net
%config(noreplace) %{_sysconfdir}/amd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/amd
%{_unitdir}/amd.service
%{_infodir}/*info*.gz
%{_libdir}/libamu.so*

%changelog
* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.2.0-4.20140906gitbb13dea6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Ian Kent <ikent@redhat.com> - 5:6.2.0-3.20140906gitbb13dea6
- add build requires for gcc and m4.

* Tue Oct 21 2014 Ian Kent <ikent@redhat.com> - 5:6.2.0-2.20140906gitbb13dea6
- fix libtool-2.4.4 build failure, bug 1181698.

* Tue Oct 21 2014 Ian Kent <ikent@redhat.com> - 5:6.2.0-1.20140906gitbb13dea6
- add perl-Unicode-EastAsianWidth to BuildRequires.

* Tue Oct 21 2014 Ian Kent <ikent@redhat.com> - 5:6.2.0-1.20140906gitbb13dea6
- Update am-utils to current git to get needed NFSv3 functionality.

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-32
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 20 2014 Ian Kent <ikent@redhat.com> - 5:6.1.5-30
- bz1074376 - am-utils will no longer start due to missing NFSv2
  - dont background autofs umount.
  - check fh on umount succeeded.
  - handle ENOENT umount return for autofs mounts.
  - fix get_nfs_version() message.
  - fix debug log deadlock.
  - linux umount wait on ebusy.
  - make sure to remove nodes in the proper order when going down.
  - fix handle failed umount on exit.
  - fix autofs proto version define.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Apr 28 2013 Ian Kent <ikent@redhat.com> - 5:6.1.5-28
- texinfo documentation build fixes.

* Sun Apr 28 2013 Ian Kent <ikent@redhat.com> - 5:6.1.5-27
- bz955445 - am-utils package should be built with PIE flags
  - use _hardened_build flag.

* Mon Feb 18 2013 Ian Kent <ikent@redhat.com> - 5:6.1.5-26
- add BuildRequires for texinfo.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Aug 22 2012 Václav Pavlín <vpavlin@redhat.com> - 5:6.1.5-24
- Scriptlets replaced with new systemd macros (#850023)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 24 2012 Karel Zak <kzak@redhat.com> - 5:6.1.5-22
- fix #784235 - amd immediately exits after starting with systemd

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Sep 09 2011 Tom Callaway <spot@fedoraproject.org> - 5:6.1.5-20
- add missing systemd scriptlets

* Thu Sep 08 2011 Tom Callaway <spot@fedoraproject.org> - 5:6.1.5-19
- convert from sysvinit to systemd

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Oct  6 2010 Karel Zak <kzak@redhat.com> 5:6.1.5-17
- fix #602938 - am-utils fails on f13 with amfs_toplvl_mount
- fix #640383 - am-utils doesn't work in Fedora 13

* Mon Mar  1 2010 Karel Zak <kzak@redhat.com> 5:6.1.5-16
- fix #566711 - am-utils: incorrect use of tcp_wrapper

* Wed Feb 24 2010 Karel Zak <kzak@redhat.com> 5:6.1.5-15
- fix #523221 - initscript collected problems LSB-compilant

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5:6.1.5-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec  2 2008 Karel Zak <kzak@redhat.com> 5:6.1.5-12
- fix #450754 - Amd does not work with 2.6.25 (thanks to Philippe Troin)

* Thu May 29 2008 Karel Zak <kzak@redhat.com> 5:6.1.5-11
- review & cleanup init script

* Thu May 29 2008 Karel Zak <kzak@redhat.com> 5:6.1.5-10
- fix #435420 - CVE-2008-1078 am-utils: insecure usage of temporary files

* Tue May 20 2008 Karel Zak <kzak@redhat.com> 5:6.1.5-9
- spec file cleanup according to rpmlint
- fix autotools stuff

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 5:6.1.5-8
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 6.1.5-7
 - Rebuild for deps

* Tue Mar 13 2007 Karel Zak <kzak@redhat.com> 5:6.1.5-6
- fix #223675 - am-utils: non-failsafe install-info
- fix #231843 - missing build dependency on tcp_wrappers
- cleanup spec file

* Mon Dec 18 2006 Karel Zak <kzak@redhat.com> 5:6.1.5-5
- fix #219437 - amd: stopping service will pop up an error dialog in
                system-config-services app.
- fix build (m4 stuff) of the package (UTS_RELEASE macro has been removed
                from the latest kernel-headers)

* Tue Aug 24 2006 Karel Zak <kzak@redhat.com> 5:6.1.5-4
- fix #203193 - tmpfile usage
- fix #202180 - amd service doesn't work

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 5:6.1.5-3
- rebuild
- Add missing br flex

* Thu Jun 01 2006 Peter Vrabec <pvrabec@redhat.com> 5:6.1.5-2
- force to use HAVE_LINUX_NFS_MOUNT_H macro, because linux/nfs_mount.h
  check in configure fails on s390x

* Mon May 29 2006 Peter Vrabec <pvrabec@redhat.com> 5:6.1.5-1
- upgrade
- add build depency

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5:6.1.3-1.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5:6.1.3-1.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Oct 20 2005 Peter Vrabec <pvrabec@redhat.com> 6.1.3-1
- upgrade

* Wed Oct 04 2005 Peter Vrabec <pvrabec@redhat.com> 6.1.2.1-1
- upgrade
- fix amd shutdown(#158268,#54246)
- enhancement, /host/localhost and /host/<localmachinename>
  are symlinks to / (#11843)

* Thu Aug 25 2005 Peter Vrabec <pvrabec@redhat.com> 6.1.1-2
- use generic linux/nfs_mount.h check

* Fri Aug 19 2005 Peter Vrabec <pvrabec@redhat.com> 6.1.1-1
- upgrade 6.1.1

* Wed Aug 17 2005 Peter Vrabec <pvrabec@redhat.com> 6.0.9-13
- fix the regression introduced with (#143118) fix

* Thu Mar 24 2005 Peter Vrabec <pvrabec@redhat.com> 6.0.9-12
- fix the am-utils part of #143118 by implementing the util-linux
  mtab locking scheme into am-utils automounter, patch and testing
  by Daniel Berrange <berrange@redhat.com>, improved locking
  algorithm by <prockai@redhat.com> (which allows for several
  hundred or even thousand of parallel makes to finish
  successfully and keep /etc/mtab in sync with /proc/mounts  as well)

* Thu Mar 17 2005 Peter Vrabec <pvrabec@redhat.com>
- rebuild by gcc4

* Tue Oct 12 2004 Adrian Havill <havill@redhat.com> 6.0.9-10
- cleanup %%pre script so amd.conf won't get stat()ed if it doesn't
  exist (#126656)

* Wed Sep  1 2004 Nalin Dahyabhai <nalin@redhat.com> 6.0.9-9
- really fix %%preun this time

* Tue Aug 31 2004 Nalin Dahyabhai <nalin@redhat.com> 6.0.9-8
- rebuild

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Mar 15 2004 Nalin Dahyabhai <nalin@redhat.com>
- fix incorrect invocation of test in %%pre and %%preun

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Nov 11 2003 Nalin Dahyabhai <nalin@redhat.com> 6.0.9-5
- change permissions on /etc/sysconfig/amd from 0755 to 0644 (#109681)

* Tue Aug  5 2003 Elliot Lee <sopwith@redhat.com> 6.0.9-4
- Fix libtool

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 04 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- add symlink to shared lib

* Fri Jan 31 2003 Nalin Dahyabhai <nalin@redhat.com> 6.0.9-1
- update to 6.0.9
- disable RPM's internal dependency calculation so that we can filter out
  dependencies which are expected to be filled in by the site administrator

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan  7 2003 Nalin Dahyabhai <nalin@redhat.com> 6.0.8-3
- rebuild

* Wed Oct 30 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.8-1
- update to 6.0.8

* Tue Aug 27 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-9
- rebuild

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed May 29 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-7
- adjust the perl reqs so that the lostaltmail config files aren't required
  by RPM

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May  9 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-5
- rebuild in new environment

* Fri Feb 22 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-4
- rebuild in new environment

* Sat Jan 26 2002 Jeff Johnson <jbj@redhat.com>
- add Provides: to white out certain perl Requires:

* Wed Jan 23 2002 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-2
- rebuild in new environment
- require gdbm-devel at build-time instead of db1-devel

* Thu Sep  6 2001 Nalin Dahyabhai <nalin@redhat.com> 6.0.7-1
- update to 6.0.7, fixing EIO on access bugs (#53251)
- back out nfs3 patch; no longer needed for current kernels
- don't explicitly strip binaries; let the buildroot policies handle it

* Wed Jul 18 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild

* Mon Jun 25 2001 Nalin Dahyabhai <nalin@redhat.com>
- add BuildPrereq: db1-devel (#44987)
- use FHS macros
- return error codes correctly from init script (#44597)

* Tue May 22 2001 Nalin Dahyabhai <nalin@redhat.com>
- update to 6.0.6

* Sat Apr  7 2001 Nalin Dahyabhai <nalin@redhat.com>
- update to 6.0.5
- remove /net from the default MOUNTPTS

* Tue Mar 13 2001 Nalin Dahyabhai <nalin@redhat.com>
- use MOUNTPTS when starting

* Fri Mar  2 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Wed Feb 14 2001 Nalin Dahyabhai <nalin@redhat.com>
- redo i18n for the init script (#24082)

* Tue Jan 23 2001 Nalin Dahyabhai <nalin@redhat.com>
- re-do workaround from advice from the am-utils maintainers
- redo i18n for the init script

* Sat Jan 20 2001 Nalin Dahyabhai <nalin@redhat.com>
- work around clash with nfs3_fh definition in 2.4

* Tue Jan 16 2001 Nalin Dahyabhai <nalin@redhat.com>
- gettextize the init script (#24087)

* Tue Dec 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- add ldconfig to %%postun
- chuck the hesiod patch -- new bind-utils doesn't have the support for it

* Fri Sep  8 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Sat Jul 15 2000 Bill Nottingham <notting@redhat.com>
- move initscript back

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jul  6 2000 Nalin Dahyabhai <nalin@redhat.com>
- only create /var/lock/subsys/amd if startup succeeds
- revamp shutdown procedure to minimize time spent just spinning
- change initscripts dependency to /etc/init.d

* Tue Jul  4 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- delete noreplace from initscript

* Wed Jun 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix postun script
- add requires: initscripts

* Tue Jun 27 2000 Nalin Dahyabhai <nalin@redhat.com>
- remove unnecessary libamu.so symlink

* Mon Jun 26 2000 Nalin Dahyabhai <nalin@redhat.com>
- move init script to /etc/init.d
- add URL: tag

* Wed Jun 21 2000 Preston Brown <pbrown@redhat.com>
- noreplace config files
- gracefully stop/restart service

* Fri Jun 16 2000 Matt Wilson <msw@redhat.com>
- FHS paths
- 6.0.4 snapshot (as it builds against kernel 2.4 headers)

* Wed Feb 16 2000 Cristian Gafton <gafton@redhat.com>
- version 6.0.3
- enhance init script to be more wait4amd2die-like
- make default map type to be file (#9185)
- get rid of the kludges

* Thu Feb 03 2000 Cristian Gafton <gafton@redhat.com>
- man pages are compressed
- version 6.0.2
- fix descriptions

* Mon Sep 13 1999 Cristian Gafton <gafton@redhat.com>
- version 6.0.1 final

* Tue Aug 24 1999 Cristian Gafton <gafton@redhat.com>
- remove the noldap patch
- add amd.net file as the default config map file
- change the config file to teh new config file format instead of a
  simple map file name.
- try to avoid some damage with a new %%pre script
- prereq grep now
- modify the init file so it calls amd -F /etc/amd.conf now

* Tue Aug 24 1999 Bill Nottingham <notting@redhat.com>
- update to 6.0.1s11

* Fri Jun 19 1999 Bill Nottingham <notting@redhat.com>
- don't run by default

* Mon May 31 1999 Kenneth Skaar <kenneths@regina.uio.no>
- Fixed amd -F core dump and related dumps by other programs

* Thu Apr 08 1999 Preston Brown <pbrown@redhat.com>
- kill -HUP on reload, restart does a real restart.

* Fri Mar 26 1999 Bill Nottingham <notting@redhat.com>
- twiddle an echo in initscript

* Tue Mar 23 1999 Cristian Gafton <gafton@redhat.com>
- version 6.0 proper
- Serial:1 because to enforce versioning

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com>
- auto rebuild in the new build environment (release 6)

* Wed Jan 06 1999 Cristian Gafton <gafton@redhat.com>
- rebuild for glibc 2.1
- strip all binaries

* Thu Aug 13 1998 Jeff Johnson <jbj@redhat.com>
- add missing ':' to default 'opts:=nosuid,nodev'
- install info pages

* Mon Jul 13 1998 Cristian Gafton <gafton@redhat.com>
- added the NIS support that the broken configure script failed to detect

* Tue May 05 1998 Cristian Gafton <gafton@redhat.com>
- disabled autofs support on alpha
- run ldconfig in postinstall

* Mon May 04 1998 Cristian Gafton <gafton@redhat.com>
- new package to replace the old and unmaintained amd
