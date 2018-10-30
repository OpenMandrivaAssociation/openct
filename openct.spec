%define major 1
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

Summary:	Smartcard Terminal Tnterface
Name:		openct
Version:	0.6.20
Release:	15
License:	LGPLv2+
Group:		System/Servers
Url:		http://www.opensc.org
Source0:	http://www.opensc-project.org/files/openct/%{name}-%{version}.tar.gz
Patch0:		initscript-lsb.patch
BuildRequires:	flex
BuildRequires:	libltdl-devel
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(libpcsclite)
BuildRequires:	pkgconfig(udev)
Requires(pre,post):	rpm-helper

%description
This is OpenCT, a middleware framework for smart card terminals.

%package -n %{libname}
Summary:	Library for accessing Smartcards
Group:		System/Libraries

%description -n %{libname}
These are the shared libraries for the smartcard terminal middleware
OpenCT.
If you want to compile applications using this library, you also need
the %{name}-devel package.

%package -n %{devname}
Summary:	Supplementary files for developing %{name} applications
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}

%description	-n %{devname}
This package includes the development files for %{name}.

%prep
%setup -q
%apply_patches
# fix lib64 std rpaths and other weirdness
sed -i -e 's|/lib /usr/lib\b|/%{_lib} %{_libdir}|' \
       -e 's|^usrsbindir=.*$|usrsbindir="%{_sbindir}"|' \
       -e 's|^usrlibdir=.*$|usrlibdir="%{_libdir}"|' configure 
sed -i -e 's|^\([A-Z]\)|# \1|' etc/reader.conf.in

%build
%configure2_5x \
	--disable-static \
	--enable-pcsc \
	--without-bundle \
	--localstatedir=%{_var}
%make

sed -i -e "s,^DRIVER=,DRIVERS=," etc/openct.udev

%check
make -k check

%install
mkdir -p %{buildroot}%{_sysconfdir}
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

%preun 
%_preun_service openct

%post 
%_post_service openct

%files
%doc NEWS LGPL-2.1
%doc doc/
%{_bindir}/*
%{_sbindir}/*
%{_var}/run/*
%{_mandir}/man1/*
%{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/openct.conf
%config(noreplace) %{_sysconfdir}/udev/rules.d/70-%{name}.rules

%files -n %{libname}
%{_libdir}/libopenct.so.%{major}*

%files -n %{devname}
%doc TODO
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/*

