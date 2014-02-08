%define lib_major 1
%define lib_name %mklibname %{name} %{lib_major}
%define libdevel %mklibname -d %{name}
%define olddevel %mklibname -d %{name} 1

Summary:	Smartcard Terminal Tnterface
Name:		openct
Version:	0.6.20
Release:	5
License:	LGPLv2+
Group:		System/Servers
URL:		http://www.opensc.org
Source0:	http://www.opensc-project.org/files/openct/%{name}-%{version}.tar.gz
Patch0:		initscript-lsb.patch
BuildRequires:	pkgconfig(libpcsclite)
BuildRequires:	flex
BuildRequires:	pkgconfig(libusb)
BuildRequires:	libltdl-devel
BuildRequires:	udev
Requires:	%{lib_name} = %{version}
Requires(pre):  rpm-helper
Requires(post): rpm-helper

%description
This is OpenCT, a middleware framework for smart card terminals.

%package	-n %{lib_name}
Group:		System/Libraries
Summary:	Library for accessing Smartcards
Provides:	libopenct = %{version}-%{release}

%description	-n %{lib_name}
These are the shared libraries for the smartcard terminal middleware
OpenCT.
If you want to compile applications using this library, you also need
the %{name}-devel package.

%package	-n %{libdevel}
Group:	Development/C
Summary:	Supplementary files for developing %{name} applications
Provides: 	libopenct-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}-%{release}

%description	-n %{libdevel}
Header files, static libraries, and documentation for %{name}.

%prep
%setup -q
%patch0 -p1
# fix lib64 std rpaths and other weirdness
sed -i -e 's|/lib /usr/lib\b|/%{_lib} %{_libdir}|' \
       -e 's|^usrsbindir=.*$|usrsbindir="%{_sbindir}"|' \
       -e 's|^usrlibdir=.*$|usrlibdir="%{_libdir}"|' configure 
sed -i -e 's|^\([A-Z]\)|# \1|' etc/reader.conf.in

%build
%configure2_5x \
    --enable-pcsc \
    --without-bundle \
    --localstatedir=%{_var}
%make

sed -i -e "s,^DRIVER=,DRIVERS=," etc/openct.udev

%check
make -k check

%install
%makeinstall_std 
#install -d %{buildroot}/%{_sysconfdir}/hotplug/usb
install -d %{buildroot}/%{_initrddir}
install -d %{buildroot}/%{_var}/run/openct
cp %{_builddir}/%{name}-%{version}/%{_sysconfdir}/openct.conf %{buildroot}/%{_sysconfdir}

#perl -pi -e "s|#! /bin/sh|#! /bin/sh\n#\n# This shell script takes care of starting and stopping\n# openct server\n#\n# chkconfig: 345 39 50\n# description: Smartcard Terminal Tnterface|" %{_builddir}/%{name}-%{version}/%{_sysconfdir}/init-script 
install -m755 %{_builddir}/%{name}-%{version}/%{_sysconfdir}/init-script %{buildroot}/%{_initrddir}/%{name}

install -d -m755 %{buildroot}%{_sysconfdir}/udev/rules.d
perl -pi -e 's!/etc/hotplug/usb/%{name}!%{name}!' etc/openct.udev
install -m 0644 etc/openct.udev %{buildroot}%{_sysconfdir}/udev/rules.d/70-%{name}.rules
#install -d -m755 %{buildroot}/%{_lib}/udev/
#install -m755 etc/hotplug.openct %{buildroot}/%{_lib}/udev/%{name}

# reference to home or tmp
rm -rf %{buildroot}/%{_libdir}/libifd.la

%preun 
%_preun_service openct

%post 
%_post_service openct

%files
%doc NEWS TODO LGPL-2.1
%doc doc/
%{_bindir}/*
%{_sbindir}/*
%{_var}/run/*
%{_mandir}/man1/*
%{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/openct.conf
%config(noreplace) %{_sysconfdir}/udev/rules.d/70-%{name}.rules

%files -n %{lib_name}
%doc TODO
%{_libdir}/*.so.%{lib_major}*

%files -n %{libdevel}
%doc TODO
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/*.pc
%{_includedir}/*


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.6.20-3mdv2011.0
+ Revision: 666950
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.6.20-2mdv2011.0
+ Revision: 607015
- rebuild

* Mon Feb 22 2010 Emmanuel Andry <eandry@mandriva.org> 0.6.20-1mdv2010.1
+ Revision: 509758
- New version 0.6.20

* Thu Jan 07 2010 Frederik Himpe <fhimpe@mandriva.org> 0.6.19-1mdv2010.1
+ Revision: 487338
- update to new version 0.6.19

* Thu Oct 01 2009 Funda Wang <fwang@mandriva.org> 0.6.18-1mdv2010.0
+ Revision: 451961
- new version 0.6.18

* Fri Sep 25 2009 Frederik Himpe <fhimpe@mandriva.org> 0.6.17-1mdv2010.0
+ Revision: 449250
- update to new version 0.6.17

* Sun May 10 2009 Frederik Himpe <fhimpe@mandriva.org> 0.6.16-1mdv2010.0
+ Revision: 374050
- Update to new version 0.6.16
- Rediff init script patch

* Fri Jan 30 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.6.15-3mdv2009.1
+ Revision: 335483
- Added lsb header to initscript (#47299).

* Wed Jan 28 2009 Funda Wang <fwang@mandriva.org> 0.6.15-2mdv2009.1
+ Revision: 334835
- fix bug https://bugzilla.redhat.com/show_bug.cgi?id=480756

* Tue Oct 14 2008 Funda Wang <fwang@mandriva.org> 0.6.15-1mdv2009.1
+ Revision: 293498
- new version 0.6.15

* Tue Jul 08 2008 Oden Eriksson <oeriksson@mandriva.com> 0.6.14-4mdv2009.0
+ Revision: 232815
- fix build

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Mar 04 2008 Oden Eriksson <oeriksson@mandriva.com> 0.6.14-2mdv2008.1
+ Revision: 179108
- rebuild

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Aug 30 2007 Andreas Hasenack <andreas@mandriva.com> 0.6.14-1mdv2008.0
+ Revision: 76267
- updated to 0.6.14, which should fix udev/hotplug things
- adapted to new devel library policy


* Mon Feb 05 2007 Andreas Hasenack <andreas@mandriva.com> 0.6.11-3mdv2007.0
+ Revision: 116213
- s/DRIVER/DRIVERS/ in udev file (#28549)

* Mon Jan 15 2007 Andreas Hasenack <andreas@mandriva.com> 0.6.11-2mdv2007.1
+ Revision: 109063
- fixed rpm group for devel package (#28155)

* Wed Nov 22 2006 Andreas Hasenack <andreas@mandriva.com> 0.6.11-1mdv2007.1
+ Revision: 86104
- updated to version 0.6.11
- this one got rid of hotplug it seems
- fix filename
- updated to version 0.6.10
- Import openct

* Mon Jul 24 2006 Emmanuel Andry <eandry@mandriva.org> 0.6.8-1mdv2007.0
- New release 0.6.8

* Tue Jun 27 2006 Olivier Blin <oblin@mandriva.com> 0.6.7-6mdv2007.0
- move udev helper in /$lib/udev
- fix udev rules to call correct helper
- fix udev rules permission

* Wed May 24 2006 Andreas Hasenack <andreas@mandriva.com> 0.6.7-5mdk
- imported fixes from CS4:
  - more fixes for the wrong soname problem
- when introducing version 0.6.7 I forgot to reset the release numbering
  back to 1 (it remained at 4, despite what the changelog entry below says),
  so we jumped to 5mdk now :(

* Tue May 16 2006 Andreas Hasenack <andreas@mandriva.com> 0.6.7-1mdk
- updated to version 0.6.7
- using upstream provided udev rules
- license is LGPL (although some files are still BSD, the majority of them
  is now LGPL)

* Sat May 13 2006 Olivier Blin <oblin@mandriva.com> 0.6.6-4mdk
- convert usermap to udev rules (the usermap wasn't even installed
  previously, so nothing was done on hotplug)
- drop config flag for init script

* Wed Nov 23 2005 Andreas Hasenack <andreas@mandriva.com> 0.6.6-3mdk
- using /var as localstatedir (so that /var/run/openct works)

* Mon Nov 07 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 0.6.6-2mdk
- add BuildRequires: libltdl-devel

* Sun Nov 06 2005 Michael Scherer <misc@mandriva.org> 0.6.6-1mdk
- New release 0.6.6
- mkrel
- fix prereq
- add %%check

* Fri Mar 04 2005 Lenny Cartier <lenny@mandrakesoft.com> 0.6.2-1mdk
- from Udo Rader <udo.rader@bestsolution.at> : 
	- new upstream version

* Mon Nov 01 2004 Christiaan Welvaart <cjw@daneel.dyndns.org> 0.1.0-3mdk
- add BuildRequires: flex libusb-devel

