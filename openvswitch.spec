#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

# set kernel_builtin to true for kernels with openvswitch module (>= 3.3)
%define		kernel_builtin	%(echo %{_kernel_ver} | awk '{ split($0, v, "."); vv=v[1]*1000+v[2]; if (vv >= 3003) print 1; else print 0 }')
#'
%if %{kernel_builtin} == 1
%undefine	with_kernel
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	1
%define		pname	openvswitch
Summary:	Production Quality, Multilayer Open Virtual Switch
#Summary(pl.UTF-8):	-
Name:		%{pname}%{_alt_kernel}
Version:	1.4.1
Release:	%{rel}
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	http://openvswitch.org/releases/%{pname}-%{version}.tar.gz
# Source0-md5:	6f0e1a3ac032bfacff290016583f2b0f
Source1:	ifdown-ovs
Source2:	ifup-ovs
Source3:	README.PLD
Source4:	%{pname}.logrotate
Source5:	%{pname}.tmpfiles
Source6:	%{pname}.sysconfig
Source7:	%{pname}.init
#Source8:	openvswitch-controller.init
#Source9:	openvswitch-ipsec.init
Source10:	%{pname}.service
Source11:	ovsdbmonitor.desktop
Patch0:		linux-3.3.patch
Patch1:		ovsdbmonitor-move-to-its-own-data-directory.patch
URL:		http://openvswitch.org/
BuildRequires:	Zope-Interface
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	graphviz
BuildRequires:	groff
BuildRequires:	openssl-devel
BuildRequires:	openssl-tools
BuildRequires:	pkgconfig
BuildRequires:	python-PyQt4-devel
BuildRequires:	python-PyQt4-devel-tools
BuildRequires:	python-TwistedConch
BuildRequires:	python-TwistedCore
BuildRequires:	python-distribute
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
%endif
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	python-modules
Requires:	rc-scripts
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{pname}-%{version}-root-%(id -u -n)

%description
Open vSwitch is a production quality, multilayer virtual switch
licensed under the open source Apache 2.0 license. It is designed to
enable massive network automation through programmatic extension,
while still supporting standard management interfaces and protocols
(e.g. NetFlow, sFlow, SPAN, RSPAN, CLI, LACP, 802.1ag). In addition,
it is designed to support distribution across multiple physical
servers similar to VMware's vNetwork distributed vswitch or Cisco's
Nexus 1000V.

#%description -l pl.UTF-8

%package -n python-openvswitch
Summary:	Open vSwitch python bindings
Group:		Development/Languages/Python
Requires:	python-modules

%description -n python-openvswitch
Python bindings for the Open vSwitch database

%package -n ovsdbmonitor
Summary:	Open vSwitch graphical monitoring tool
Group:		Networking/Admin
Requires:	Zope-Interface
Requires:	python-PyQt4-devel-tools
Requires:	python-TwistedConch
Requires:	python-TwistedCore
Requires:	python-modules
Requires:	python-openvswitch = %{version}-%{release}

%description -n ovsdbmonitor
A GUI tool for monitoring and troubleshooting local or remote Open
vSwitch installations. It presents GUI tables that graphically
represent an Open vSwitch kernel flow table (similar to "ovs-dpctl
dump-flows") and Open vSwitch database contents (similar to "ovs-vsctl
list <table>").

%package test
Summary:	Open vSwitch test package
Group:		Networking/Admin
Requires:	python-modules
Requires:	python-openvswitch = %{version}-%{release}

%description test
This package contains utilities that are useful to diagnose
performance and connectivity issues in Open vSwitch setup.

%package -n kernel%{_alt_kernel}-net-openvswitch
Summary:	Linux driver for openvswitch
Summary(pl.UTF-8):	Sterownik dla Linuksa do openvswitch
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-openvswitch
This is driver for openvswitch for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-openvswitch -l pl.UTF-8
Sterownik dla Linuksa do openvswitch.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
%patch1 -p1
cp %{SOURCE3} .

%build
%{__aclocal} -I m4
%{__automake}
%{__autoconf}
%configure \
%if %{with kernel}
	--with-linux=%{_kernelsrcdir} \
	--with-linux-source=%{_kernelsrcdir}
%endif

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{py_sitescriptdir},%{systemdunitdir},%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/lib/rc-scripts} \
	$RPM_BUILD_ROOT{%{_desktopdir},%{_datadir}/%{pname}/pki}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/lib/rc-scripts/ifdown-ovs
install -p %{SOURCE2} $RPM_BUILD_ROOT/lib/rc-scripts/ifup-ovs
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/openvswitch
install -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/openvswitch.conf
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/sysconfig/openvswitch
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/openvswitch
install -p %{SOURCE10} $RPM_BUILD_ROOT%{systemdunitdir}/openvswitch.service
install -p %{SOURCE11} $RPM_BUILD_ROOT%{_desktopdir}

%{__mv} $RPM_BUILD_ROOT%{_datadir}/%{pname}/python/{ovs,ovstest} $RPM_BUILD_ROOT%{py_sitescriptdir}
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/%{pname}/python

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}

%py_ocomp $RPM_BUILD_ROOT%{_datadir}/ovsdbmonitor
%py_comp $RPM_BUILD_ROOT%{_datadir}/ovsdbmonitor
%endif

%if %{with kernel}
cd datapath/linux
%install_kernel_modules -m brcompat_mod -d kernel/net/openvswitch
%install_kernel_modules -m openvswitch_mod -d kernel/net/openvswitch
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add openvswitch
%service openvswitch restart
%systemd_post openvswitch.service

%preun
if [ "$1" = "0" ]; then
	%service -q openvswitch stop
	/sbin/chkconfig --del openvswitch
fi
%systemd_preun openvswitch.service

%postun
%systemd_reload

%post	-n kernel%{_alt_kernel}-net-openvswitch
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-openvswitch
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS DESIGN INSTALL.KVM INSTALL.SSL INSTALL.bridge INSTALL.userspace NEWS README
%doc REPORTING-BUGS WHY-OVS README.PLD
%attr(755,root,root) /lib/rc-scripts/ifdown-ovs
%attr(755,root,root) /lib/rc-scripts/ifup-ovs
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/openvswitch
%{systemdtmpfilesdir}/openvswitch.conf
%{systemdunitdir}/openvswitch.service
%dir %{_datadir}/%{pname}
%{_datadir}/%{pname}/pki
%dir %{_datadir}/%{pname}/scripts
%attr(755,root,root) %{_datadir}/%{pname}/scripts/*
%{_datadir}/%{pname}/bugtool-plugins
%{_datadir}/%{pname}/vswitch.ovsschema

%attr(754,root,root) /etc/rc.d/init.d/openvswitch
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/openvswitch

%attr(755,root,root) %{_bindir}/ovs-appctl
%attr(755,root,root) %{_bindir}/ovs-benchmark
%attr(755,root,root) %{_bindir}/ovs-controller
%attr(755,root,root) %{_bindir}/ovs-dpctl
%attr(755,root,root) %{_bindir}/ovs-ofctl
%attr(755,root,root) %{_bindir}/ovs-parse-leaks
%attr(755,root,root) %{_bindir}/ovs-pcap
%attr(755,root,root) %{_bindir}/ovs-pki
%attr(755,root,root) %{_bindir}/ovs-tcpundump
%attr(755,root,root) %{_bindir}/ovs-vsctl
%attr(755,root,root) %{_bindir}/ovsdb-client
%attr(755,root,root) %{_bindir}/ovsdb-tool
%attr(755,root,root) %{_sbindir}/ovs-brcompatd
%attr(755,root,root) %{_sbindir}/ovs-bugtool
%attr(755,root,root) %{_sbindir}/ovs-vlan-bug-workaround
%attr(755,root,root) %{_sbindir}/ovs-vswitchd
%attr(755,root,root) %{_sbindir}/ovsdb-server
%{_mandir}/man1/ovs-benchmark.1*
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man1/ovs-tcpundump.1*
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man8/ovs-appctl.8*
%{_mandir}/man8/ovs-brcompatd.8*
%{_mandir}/man8/ovs-bugtool.8*
%{_mandir}/man8/ovs-controller.8*
%{_mandir}/man8/ovs-ctl.8*
%{_mandir}/man8/ovs-dpctl.8*
%{_mandir}/man8/ovs-ofctl.8*
%{_mandir}/man8/ovs-parse-leaks.8*
%{_mandir}/man8/ovs-pki.8*
%{_mandir}/man8/ovs-vlan-bug-workaround.8*
%{_mandir}/man8/ovs-vlan-test.8*
%{_mandir}/man8/ovs-vsctl.8*
%{_mandir}/man8/ovs-vswitchd.8*

%files -n python-openvswitch
%defattr(644,root,root,755)
%dir %{py_sitescriptdir}/ovs
%{py_sitescriptdir}/ovs/*.py*
%dir %{py_sitescriptdir}/ovs/db
%{py_sitescriptdir}/ovs/db/*.py*

%files -n ovsdbmonitor
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ovsdbmonitor
%{_datadir}/ovsdbmonitor
%{_desktopdir}/ovsdbmonitor.desktop
%{_mandir}/man1/ovsdbmonitor.1*

%files test
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ovs-test
%attr(755,root,root) %{_bindir}/ovs-vlan-test
%{py_sitescriptdir}/ovstest
%{_mandir}/man8/ovs-test.8*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-openvswitch
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/net/openvswitch
/lib/modules/%{_kernel_ver}/kernel/net/openvswitch/*.ko*
%endif
