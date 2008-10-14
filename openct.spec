%define lib_major 1
%define lib_name %mklibname %{name} %{lib_major}
%define libdevel %mklibname -d %{name}
%define olddevel %mklibname -d %{name} 1

Summary:	Smartcard Terminal Tnterface
Name:		openct
Version:	0.6.15
Release:	%mkrel 1
License:	LGPL
Group:		System/Servers
URL:		http://www.opensc.org
Source0:	http://www.opensc.org/files/%{name}-%{version}.tar.gz
BuildRequires:	pcsc-lite-devel flex libusb-devel
BuildRequires:	libltdl-devel udev-tools
Requires:	%{lib_name} = %{version}
Requires(pre):  rpm-helper
Requires(post): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This is OpenCT, a middleware framework for smart card terminals.

%package	-n %{lib_name}
Group:		System/Libraries
Summary:	Library for accessing Smartcards
Provides: libopenct = %{version}-%{release}
# major 0 was wrong
Obsoletes: libopenct0 <= 0.6.6-4mdk
Obsoletes: libopenct <= 0.6.6-4mdk

%description	-n %{lib_name}
These are the shared libraries for the smartcard terminal middleware
OpenCT.
If you want to compile applications using this library, you also need
the %{name}-devel package.

%package	-n %{libdevel}
Requires:	%{lib_name} = %{version}
Group:		Development/C
Summary:	Supplementary files for developing %{name} applications
Provides: 	libopenct-devel = %{version}-%{release}
Obsoletes:	libopenct0-devel <= 0.6.6-4mdk
Obsoletes:	libopenct-devel <= 0.6.6-4mdk
Obsoletes:      %{olddevel} < 0.6.14

%description	-n %{libdevel}
Header files, static libraries, and documentation for %{name}.

%prep
%setup -q 

%build
%configure2_5x \
    --enable-pcsc \
    --without-bundle \
    --localstatedir=%{_var}
make

sed -i -e "s,^DRIVER=,DRIVERS=," etc/openct.udev

%check
make -k check

%install
rm -rf %{buildroot}

%makeinstall_std 
#install -d %{buildroot}/%{_sysconfdir}/hotplug/usb
install -d %{buildroot}/%{_initrddir}
install -d %{buildroot}/%{_var}/run/openct
cp %{_builddir}/%{name}-%{version}/%{_sysconfdir}/openct.conf %{buildroot}/%{_sysconfdir}

perl -pi -e "s|#! /bin/sh|#! /bin/sh\n#\n# This shell script takes care of starting and stopping\n# openct server\n#\n# chkconfig: 345 39 50\n# description: Smartcard Terminal Tnterface|" %{_builddir}/%{name}-%{version}/%{_sysconfdir}/init-script 
cp %{_builddir}/%{name}-%{version}/%{_sysconfdir}/init-script %{buildroot}/%{_initrddir}/%{name}

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

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{lib_name}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{lib_name}
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
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
%defattr(-,root,root)
%doc TODO
%{_libdir}/*.so.*

%files -n %{libdevel}
%defattr(-,root,root)
%doc TODO
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/*.pc
%{_includedir}/*
