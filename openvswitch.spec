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

%define		rel	0.1
Summary:	Production Quality, Multilayer Open Virtual Switch
#Summary(pl.UTF-8):	-
Name:		openvswitch
Version:	1.4.0
Release:	%{rel}
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	http://openvswitch.org/releases/%{name}-%{version}.tar.gz
# Source0-md5:	3847c60af329bfe81ff7220b9f489fa5
Source1:	ifdown-ovs
Source2:	ifup-ovs
Source3:	README.PLD
Source4:	%{name}.logrotate
Source5:	%{name}.tmpfiles
Source6:	%{name}.sysconfig
Source7:	%{name}.init
#Source8:	openvswitch-controller.init
#Source9:	openvswitch-ipsec.init
Source10:	%{name}.service
URL:		http://openvswitch.org/
BuildRequires:	python-distribute
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
%endif
Requires(post,preun):	/sbin/chkconfig
#BuildRequires:	-
Requires:	python-modules
Requires:	rc-scripts
#Requires(postun):	-
#Requires(pre,post):	-
#Requires(preun):	-
#Requires:	-
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%package test
Summary:	Open vSwitch test package
Group:		Networking/Admin
Requires:	python-modules

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
%setup -q
cp %{SOURCE3} .

%build
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
	$RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/lib/rc-scripts}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/lib/rc-scripts/ifdown-ovs
install -p %{SOURCE2} $RPM_BUILD_ROOT/lib/rc-scripts/ifup-ovs
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/openvswitch
install -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/openvswitch.conf
install -p %{SOURCE6} $RPM_BUILD_ROOT/etc/sysconfig/openvswitch
install -p %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/openvswitch
install -p %{SOURCE10} $RPM_BUILD_ROOT%{systemdunitdir}/openvswitch.service

%{__mv} $RPM_BUILD_ROOT%{_datadir}/%{name}/python/{ovs,ovstest} $RPM_BUILD_ROOT%{py_sitescriptdir}
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/%{name}/python

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
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
%{_datadir}/%{name}

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
%attr(755,root,root) %{_bindir}/ovs-vlan-test
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
%dir %{py_sitescriptdir}/ovs
%{py_sitescriptdir}/ovs/*.py*
%dir %{py_sitescriptdir}/ovs/db
%{py_sitescriptdir}/ovs/db/*.py*

%files test
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ovs-test
%{py_sitescriptdir}/ovstest
%{_mandir}/man8/ovs-test.8*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-openvswitch
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/openvswitch/*.ko*
%endif
