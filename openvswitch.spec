# TODO:
# - verify all init scripts still work
#
# warning: Installed (but unpackaged) file(s) found:
#	/etc/bash_completion.d/ovs-appctl-bashcomp.bash
#	/etc/bash_completion.d/ovs-vsctl-bashcomp.bash
#	/usr/bin/ovn-controller
#	/usr/bin/ovn-controller-vtep
#	/usr/bin/ovn-detrace
#	/usr/bin/ovn-docker-overlay-driver
#	/usr/bin/ovn-docker-underlay-driver
#	/usr/bin/ovn-nbctl
#	/usr/bin/ovn-northd
#	/usr/bin/ovn-sbctl
#	/usr/bin/ovn-trace
#	/usr/bin/ovs-docker
#	/usr/bin/ovs-tcpdump
#	/usr/bin/ovs-testcontroller
#	/usr/bin/vtep-ctl
#	/usr/share/man/man1/ovn-detrace.1.gz
#	/usr/share/man/man5/ovn-nb.5.gz
#	/usr/share/man/man5/ovn-sb.5.gz
#	/usr/share/man/man5/vtep.5.gz
#	/usr/share/man/man7/ovn-architecture.7.gz
#	/usr/share/man/man7/ovs-fields.7.gz
#	/usr/share/man/man8/ovn-controller-vtep.8.gz
#	/usr/share/man/man8/ovn-controller.8.gz
#	/usr/share/man/man8/ovn-ctl.8.gz
#	/usr/share/man/man8/ovn-nbctl.8.gz
#	/usr/share/man/man8/ovn-northd.8.gz
#	/usr/share/man/man8/ovn-sbctl.8.gz
#	/usr/share/man/man8/ovn-trace.8.gz
#	/usr/share/man/man8/ovs-tcpdump.8.gz
#	/usr/share/man/man8/ovs-testcontroller.8.gz
#	/usr/share/man/man8/vtep-ctl.8.gz
#	/usr/share/openvswitch/ovn-nb.ovsschema
#	/usr/share/openvswitch/ovn-sb.ovsschema
#	/usr/share/openvswitch/vtep.ovsschema

#
# Conditional build:
%bcond_with	kernel		# build kernel module for flow-based switching for kernels < 4.11
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	0.1
%define		pname	openvswitch
Summary:	Production Quality, Multilayer Open Virtual Switch
#Summary(pl.UTF-8):	-
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	2.10.0
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	http://openvswitch.org/releases/%{pname}-%{version}.tar.gz
# Source0-md5:	33a55c9bac1fcaa8842f84a175e50800
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
URL:		http://openvswitch.org/
BuildRequires:	Zope-Interface
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	graphviz
BuildRequires:	groff
BuildRequires:	openssl-devel
BuildRequires:	openssl-tools
BuildRequires:	pkgconfig
BuildRequires:	python-PyQt4-devel-tools
BuildRequires:	python-TwistedConch
BuildRequires:	python-TwistedCore
BuildRequires:	python-distribute
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.701
BuildRequires:	sip-PyQt4
%if %{with kernel}
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:3.11}
%else
Requires:	uname(release) >= 3.11
%endif
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	python-modules
Requires:	rc-scripts
Requires:	systemd-units >= 38
Obsoletes:	ovsdbmonitor < 2.3.0-1
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

%package devel
Summary:	Header files and development libraries for openvswitch
Group:		Development/Libraries

%description devel
Header files and development libraries for openvswitch.

%package -n python-openvswitch
Summary:	Open vSwitch python bindings
Group:		Development/Languages/Python
Requires:	python-modules

%description -n python-openvswitch
Python bindings for the Open vSwitch database

%package test
Summary:	Open vSwitch test package
Group:		Networking/Admin
Requires:	python-modules
Requires:	python-openvswitch = %{version}-%{release}

%description test
This package contains utilities that are useful to diagnose
performance and connectivity issues in Open vSwitch setup.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-openvswitch\
Summary:	Linux driver for openvswitch\
Summary(pl.UTF-8):	Sterownik dla Linuksa do openvswitch\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-net-openvswitch\
This is driver for openvswitch for Linux.\
\
This package contains Linux module.\
\
%description -n kernel%{_alt_kernel}-net-openvswitch -l pl.UTF-8\
Sterownik dla Linuksa do openvswitch.\
\
Ten pakiet zawiera moduł jądra Linuksa.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-net-openvswitch\
%defattr(644,root,root,755)\
/etc/modprobe.d/%{_kernel_ver}/openvswitch.conf\
%dir /lib/modules/%{_kernel_ver}/kernel/net/openvswitch\
/lib/modules/%{_kernel_ver}/kernel/net/openvswitch/*.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-net-openvswitch\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-net-openvswitch\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%configure \\\
	--with-linux=%{_kernelsrcdir} \\\
	--with-linux-source=%{_kernelsrcdir}\
\
%{__make} clean\
%{__make} -C datapath/linux %{?with_verbose:V=1}\
%install_kernel_modules -D installed -s %{version} -n openvswitch -m datapath/linux/openvswitch,datapath/linux/vport-geneve,datapath/linux/vport-gre,datapath/linux/vport-lisp,datapath/linux/vport-stt,datapath/linux/vport-vxlan -d kernel/net/openvswitch\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
cp %{SOURCE3} .

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
%configure
%{__make} clean
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{py_sitescriptdir},%{systemdunitdir},%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/lib/rc-scripts} \
	$RPM_BUILD_ROOT%{_datadir}/%{pname}/pki

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/lib/rc-scripts/ifdown-ovs
install -p %{SOURCE2} $RPM_BUILD_ROOT/lib/rc-scripts/ifup-ovs
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/openvswitch
install -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/openvswitch.conf
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/sysconfig/openvswitch
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/openvswitch
install -p %{SOURCE10} $RPM_BUILD_ROOT%{systemdunitdir}/openvswitch.service

%{__mv} $RPM_BUILD_ROOT%{_datadir}/%{pname}/python/{ovs,ovstest} $RPM_BUILD_ROOT%{py_sitescriptdir}
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/%{pname}/python

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}

%py_ocomp $RPM_BUILD_ROOT%{_datadir}/ovsdbmonitor
%py_comp $RPM_BUILD_ROOT%{_datadir}/ovsdbmonitor
%endif

%if %{with kernel}
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add openvswitch
%service -n openvswitch restart
NORESTART=1
%systemd_post openvswitch.service

%preun
if [ "$1" = "0" ]; then
	%service -q openvswitch stop
	/sbin/chkconfig --del openvswitch
fi
%systemd_preun openvswitch.service

%postun
%systemd_reload

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS.rst CONTRIBUTING.rst MAINTAINERS.rst NEWS NOTICE README.rst
%doc README.PLD
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
%attr(755,root,root) %{_bindir}/ovs-dpctl
%attr(755,root,root) %{_bindir}/ovs-dpctl-top
%attr(755,root,root) %{_bindir}/ovs-l3ping
%attr(755,root,root) %{_bindir}/ovs-ofctl
%attr(755,root,root) %{_bindir}/ovs-parse-backtrace
%attr(755,root,root) %{_bindir}/ovs-pcap
%attr(755,root,root) %{_bindir}/ovs-pki
%attr(755,root,root) %{_bindir}/ovs-tcpundump
%attr(755,root,root) %{_bindir}/ovs-vsctl
%attr(755,root,root) %{_bindir}/ovsdb-client
%attr(755,root,root) %{_bindir}/ovsdb-tool
%attr(755,root,root) %{_sbindir}/ovs-bugtool
%attr(755,root,root) %{_sbindir}/ovs-vlan-bug-workaround
%attr(755,root,root) %{_sbindir}/ovs-vswitchd
%attr(755,root,root) %{_sbindir}/ovsdb-server
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man1/ovs-tcpundump.1*
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man8/ovs-appctl.8*
%{_mandir}/man8/ovs-bugtool.8*
%{_mandir}/man8/ovs-ctl.8*
%{_mandir}/man8/ovs-dpctl.8*
%{_mandir}/man8/ovs-dpctl-top.8*
%{_mandir}/man8/ovs-l3ping.8*
%{_mandir}/man8/ovs-ofctl.8*
%{_mandir}/man8/ovs-parse-backtrace.8*
%{_mandir}/man8/ovs-pki.8*
%{_mandir}/man8/ovs-vlan-bug-workaround.8*
%{_mandir}/man8/ovs-vlan-test.8*
%{_mandir}/man8/ovs-vsctl.8*
%{_mandir}/man8/ovs-vswitchd.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/openflow
%{_includedir}/openvswitch
%{_includedir}/ovn
%{_libdir}/libofproto.a
%{_libdir}/libopenvswitch.a
%{_libdir}/libovn.a
%{_libdir}/libovsdb.a
%{_libdir}/libsflow.a
%{_libdir}/libvtep.a
%{_pkgconfigdir}/libofproto.pc
%{_pkgconfigdir}/libopenvswitch.pc
%{_pkgconfigdir}/libovsdb.pc
%{_pkgconfigdir}/libsflow.pc

%files -n python-openvswitch
%defattr(644,root,root,755)
%dir %{py_sitescriptdir}/ovs
%{py_sitescriptdir}/ovs/*.py*
%dir %{py_sitescriptdir}/ovs/db
%{py_sitescriptdir}/ovs/db/*.py*
%dir %{py_sitescriptdir}/ovs/unixctl
%{py_sitescriptdir}/ovs/unixctl/*.py*

%files test
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ovs-test
%attr(755,root,root) %{_bindir}/ovs-vlan-test
%{py_sitescriptdir}/ovstest
%{_mandir}/man8/ovs-test.8*
%endif
