%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1

%define tools_version 2.1.0.2
%define linux_version 2.1.0.3

%define	progs dahdi_diag fxstest hdlcgen hdlcstress hdlctest hdlcverify patgen patlooptest pattest timertest

%define	major 2
%define libname	%mklibname tonezone %{major}
%define develname %mklibname tonezone -d

Summary:	Userspace tools and DAHDI kernel modules
Name:		dahdi
Version:	%{tools_version}
Release:	%mkrel 1
Group:		System/Kernel and hardware
License:	GPLv2 and LGPLv2
URL:		http://www.asterisk.org/
Source0:	http://downloads.digium.com/pub/telephony/dahdi-tools/dahdi-tools-%{tools_version}.tar.gz
Source1:	http://downloads.digium.com/pub/telephony/dahdi-linux/dahdi-linux-%{linux_version}.tar.gz
Source10:	http://downloads.digium.com/pub/telephony/firmware/releases/dahdi-fw-oct6114-064-1.05.01.tar.gz
Source11:	http://downloads.digium.com/pub/telephony/firmware/releases/dahdi-fw-oct6114-128-1.05.01.tar.gz
Source12:	http://downloads.digium.com/pub/telephony/firmware/releases/dahdi-fw-tc400m-MR6.12.tar.gz
Source13:	http://downloads.digium.com/pub/telephony/firmware/releases/dahdi-fw-vpmadt032-1.07.tar.gz
Patch0:		dahdi-tools-mdv.diff
BuildRequires:	newt-devel
BuildRequires:	libusb-devel
BuildConflicts:	libtonezone-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
DAHDI stands for Digium Asterisk Hardware Device Interface. This package
provides the userspace tools to configure the DAHDI kernel modules and the
kernel modules. DAHDI is the replacement for Zaptel, which must be renamed due
to trademark issues.

%package	tools
Summary:	Userspace tools to configure the DAHDI kernel modules
Group:		System/Kernel and hardware
Provides:	zaptel-tools = %{tools_version}-%{release}
Obsoletes:	zaptel-tools

%description	tools
DAHDI stands for Digium Asterisk Hardware Device Interface.

This package contains the userspace tools to configure the DAHDI kernel
modules. DAHDI is the replacement for Zaptel, which must be renamed due to
trademark issues.

The DAHDI Telephony Interface drivers is contained in the kernel-dahdi
(or dkms) package.

%package -n	%{libname}
Summary:	The shared DAHDI Library
Group:          System/Libraries

%description -n	%{libname}
DAHDI stands for Digium Asterisk Hardware Device Interface. This package
contains the userspace tools to configure the DAHDI kernel modules. DAHDI is
the replacement for Zaptel, which must be renamed due to trademark issues.

This package contains libraries for accessing DAHDI hardware.

The DAHDI drivers is contained in the kernel-dahdi (or dkms) package.

%package -n	%{develname}
Summary:	Development files for the DAHDI Library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	tonezone-devel = %{version}-%{release}
Provides:	dahdi-devel = %{version}-%{release}
Provides:	libtonezone-devel = %{version}-%{release}

%description -n	%{develname}
DAHDI stands for Digium Asterisk Hardware Device Interface. This package
contains the userspace tools to configure the DAHDI kernel modules. DAHDI is
the replacement for Zaptel, which must be renamed due to trademark issues.

This package contains the tonezone library and the development headers for
DAHDI.

%package -n	perl-Dahdi
Summary:	Interface to Dahdi information
Group:          Development/Perl

%description -n	perl-Dahdi
DAHDI stands for Digium Asterisk Hardware Device Interface. This package
contains the userspace tools to configure the DAHDI kernel modules. DAHDI is
the replacement for Zaptel, which must be renamed due to trademark issues.

This package allows access from Perl to information about Dahdi hardware and
loaded Dahdi devices.

%package -n	dkms-dahdi
Summary:	Kernel drivers for the Digium Asterisk Hardware Device Interface (DAHDI)
Group:		System/Kernel and hardware
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	dkms
Requires:	dahdi-tools >= %{tools_version}
Requires:	sethdlc >= 1.15
Provides:	dkms-zaptel = %{linux_version}-%{release}
Obsoletes:	dkms-zaptel

%description -n	dkms-dahdi
DAHDI stands for Digium Asterisk Hardware Device Interface.

This package contains the kernel modules for DAHDI. For the required 
userspace tools see the package dahdi-tools.

%prep

%setup -q -n dahdi-tools-%{tools_version} -a1
ln -s dahdi-linux-%{linux_version}/include include

for i in %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13}; do
    cp -a $i dahdi-linux-%{linux_version}/drivers/dahdi/firmware/
    tar -C dahdi-linux-%{linux_version}/drivers/dahdi/firmware -zpxf $i
done

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;
		
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p0

%{__perl} -pi -e 's/chkconfig:\s([0-9]+)\s([0-9]+)\s([0-9]+)/chkconfig: - \2 \3/' dahdi.init

%build

pushd menuselect/mxml
%configure2_5x
popd

pushd menuselect
%configure2_5x
popd

%configure2_5x \
    --disable-static \
    --with-dahdi=`pwd` \
    --with-newt=%{_prefix} \
    --with-usb=%{_prefix}

%make

for prog in %progs; do
    %make $prog
done

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{buildroot}%{_includedir}

make install config DESTDIR=%{buildroot} PERLLIBDIR=%{perl_vendorlib}

for prog in %progs; do
    install -m0755 $prog %{buildroot}%{_sbindir}/
done

# fix one conflicting file with tetex
mv %{buildroot}%{_sbindir}/patgen %{buildroot}%{_sbindir}/%{name}-patgen

find %{buildroot} -name '*.a' -exec rm -f {} ';'

ln -sf ../../..%{_datadir}/dahdi/xpp_fxloader %{buildroot}%{_sysconfdir}/hotplug/usb/xpp_fxloader

pushd dahdi-linux-%{linux_version}
    make DESTDIR=%{buildroot} \
	install-xpp-firm \
	install-firmware \
        install-include \
        install-devices \
        HOTPLUG_FIRMWARE=yes \
        DYNFS=yes \
        UDEVRULES=yes \
        DOWNLOAD=echo
popd

for file in %{buildroot}/etc/udev/rules.d/*.rules; do
  name=`basename $file`
  mv $file %{buildroot}/etc/udev/rules.d/40-$name
done

install -d %{buildroot}/usr/src/dahdi-%{linux_version}-%{release}
cp 	dahdi-linux-%{linux_version}/Makefile \
	dahdi-linux-%{linux_version}/.version \
	%{buildroot}/usr/src/dahdi-%{linux_version}-%{release}/

cp -r	dahdi-linux-%{linux_version}/build_tools \
	dahdi-linux-%{linux_version}/drivers \
	dahdi-linux-%{linux_version}/include \
	%{buildroot}/usr/src/dahdi-%{linux_version}-%{release}/

# Remove files that produce weird dependencies
rm	%{buildroot}/usr/src/dahdi-%{linux_version}-%{release}/drivers/dahdi/oct612x/get_discards

cat > %{buildroot}/usr/src/dahdi-%{linux_version}-%{release}/dkms.conf <<EOF
PACKAGE_VERSION="%{linux_version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="dahdi"
MAKE[0]="make modules KERNVER=\$kernelver DOWNLOAD=echo"
CLEAN="make KERNVER=\$kernelver clean DOWNLOAD=echo"

BUILT_MODULE_NAME[0]="dahdi"
BUILT_MODULE_LOCATION[0]="drivers/dahdi/"
DEST_MODULE_LOCATION[0]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[1]="dahdi_dummy"
BUILT_MODULE_LOCATION[1]="drivers/dahdi/"
DEST_MODULE_LOCATION[1]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[2]="dahdi_dynamic"
BUILT_MODULE_LOCATION[2]="drivers/dahdi/"
DEST_MODULE_LOCATION[2]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[3]="dahdi_dynamic_eth"
BUILT_MODULE_LOCATION[3]="drivers/dahdi/"
DEST_MODULE_LOCATION[3]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[4]="dahdi_dynamic_loc"
BUILT_MODULE_LOCATION[4]="drivers/dahdi/"
DEST_MODULE_LOCATION[4]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[5]="dahdi_echocan_jpah"
BUILT_MODULE_LOCATION[5]="drivers/dahdi/"
DEST_MODULE_LOCATION[5]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[6]="dahdi_echocan_kb1"
BUILT_MODULE_LOCATION[6]="drivers/dahdi/"
DEST_MODULE_LOCATION[6]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[7]="dahdi_echocan_mg2"
BUILT_MODULE_LOCATION[7]="drivers/dahdi/"
DEST_MODULE_LOCATION[7]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[8]="dahdi_echocan_sec"
BUILT_MODULE_LOCATION[8]="drivers/dahdi/"
DEST_MODULE_LOCATION[8]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[9]="dahdi_echocan_sec2"
BUILT_MODULE_LOCATION[9]="drivers/dahdi/"
DEST_MODULE_LOCATION[9]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[10]="dahdi_transcode"
BUILT_MODULE_LOCATION[10]="drivers/dahdi/"
DEST_MODULE_LOCATION[10]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[11]="pciradio"
BUILT_MODULE_LOCATION[11]="drivers/dahdi/"
DEST_MODULE_LOCATION[11]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[12]="tor2"
BUILT_MODULE_LOCATION[12]="drivers/dahdi/"
DEST_MODULE_LOCATION[12]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[13]="wcb4xxp"
BUILT_MODULE_LOCATION[13]="drivers/dahdi/wcb4xxp/"
DEST_MODULE_LOCATION[13]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[14]="wcfxo"
BUILT_MODULE_LOCATION[14]="drivers/dahdi/"
DEST_MODULE_LOCATION[14]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[15]="wct1xxp"
BUILT_MODULE_LOCATION[15]="drivers/dahdi/"
DEST_MODULE_LOCATION[15]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[16]="wct4xxp"
BUILT_MODULE_LOCATION[16]="drivers/dahdi/wct4xxp/"
DEST_MODULE_LOCATION[16]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[17]="wctc4xxp"
BUILT_MODULE_LOCATION[17]="drivers/dahdi/wctc4xxp/"
DEST_MODULE_LOCATION[17]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[18]="wctdm"
BUILT_MODULE_LOCATION[18]="drivers/dahdi/"
DEST_MODULE_LOCATION[18]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[19]="wctdm24xxp"
BUILT_MODULE_LOCATION[19]="drivers/dahdi/wctdm24xxp/"
DEST_MODULE_LOCATION[19]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[20]="wcte11xp"
BUILT_MODULE_LOCATION[20]="drivers/dahdi/"
DEST_MODULE_LOCATION[20]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[21]="wcte12xp"
BUILT_MODULE_LOCATION[21]="drivers/dahdi/wcte12xp/"
DEST_MODULE_LOCATION[21]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[22]="xpd_fxo"
BUILT_MODULE_LOCATION[22]="drivers/dahdi/xpp/"
DEST_MODULE_LOCATION[22]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[23]="xpd_fxs"
BUILT_MODULE_LOCATION[23]="drivers/dahdi/xpp/"
DEST_MODULE_LOCATION[23]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[24]="xpd_pri"
BUILT_MODULE_LOCATION[24]="drivers/dahdi/xpp/"
DEST_MODULE_LOCATION[24]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[25]="xpp"
BUILT_MODULE_LOCATION[25]="drivers/dahdi/xpp/"
DEST_MODULE_LOCATION[25]="/kernel/drivers/telephony/dahdi"

BUILT_MODULE_NAME[26]="xpp_usb"
BUILT_MODULE_LOCATION[26]="drivers/dahdi/xpp/"
DEST_MODULE_LOCATION[26]="/kernel/drivers/telephony/dahdi"

AUTOINSTALL=yes
EOF

# cleanup
rm -f %{buildroot}%{_sbindir}/sethdlc
rm -rf %{buildroot}/usr/lib/hotplug/firmware
rm -f drivers/dahdi/firmware/*.{bin,gz}
rm -f %{buildroot}%{_libdir}/libtonezone.so.1.0
rm -f %{buildroot}%{_libdir}/libtonezone.so.1

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre tools
%{_sbindir}/groupadd -r dahdi &>/dev/null || :
%{_sbindir}/useradd  -r -s /sbin/nologin -d /usr/share/dahdi -M \
    -c 'DAHDI User' -g dahdi dahdi &>/dev/null || :

%post tools
/sbin/chkconfig --add dahdi

%preun tools
if [ "$1" -eq "0" ]; then
    /sbin/service dahdi stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del dahdi
fi

%post -n dkms-dahdi
dkms add -m	dahdi -v %{linux_version}-%{release} --rpm_safe_upgrade
dkms build -m	dahdi -v %{linux_version}-%{release} --rpm_safe_upgrade
dkms install -m	dahdi -v %{linux_version}-%{release} --rpm_safe_upgrade --force
%_post_service dahdi

%preun -n dkms-dahdi
dkms remove -m	dahdi -v %{linux_version}-%{release} --rpm_safe_upgrade --all
%_preun_service dahdi

%pre -n dkms-dahdi
%_pre_useradd asterisk /var/lib/asterisk /bin/sh

%postun -n dkms-dahdi
%_postun_userdel asterisk

%clean
rm -rf %{buildroot}

%files tools
%defattr(-,root,root,-)
%doc README LICENSE LICENSE.LGPL
%dir %{_sysconfdir}/dahdi
%config(noreplace) %{_sysconfdir}/dahdi/init.conf
%config(noreplace) %{_sysconfdir}/dahdi/modules
%config(noreplace) %{_sysconfdir}/dahdi/system.conf
%{_sysconfdir}/hotplug/usb/xpp_fxloader
%config(noreplace) %{_sysconfdir}/hotplug/usb/xpp_fxloader.usermap
%config(noreplace) %{_sysconfdir}/modprobe.d/dahdi
%config(noreplace) %{_sysconfdir}/modprobe.d/dahdi.blacklist
%{_initrddir}/dahdi
%{_sbindir}/dahdi_cfg
%{_sbindir}/dahdi_diag
%{_sbindir}/dahdi_genconf
%{_sbindir}/dahdi_hardware
%{_sbindir}/dahdi_monitor
%{_sbindir}/dahdi_registration
%{_sbindir}/dahdi_scan
%{_sbindir}/dahdi_speed
%{_sbindir}/dahdi_test
%{_sbindir}/dahdi_tool
%{_sbindir}/dahdi-patgen
%{_sbindir}/fpga_load
%{_sbindir}/fxotune
%{_sbindir}/fxstest
%{_sbindir}/hdlcgen
%{_sbindir}/hdlcstress
%{_sbindir}/hdlctest
%{_sbindir}/hdlcverify
%{_sbindir}/lsdahdi
%{_sbindir}/patlooptest
%{_sbindir}/pattest
%{_sbindir}/timertest
%{_sbindir}/xpp_blink
%{_sbindir}/xpp_sync
%{_datadir}/dahdi/xpp_fxloader
%{_datadir}/dahdi/waitfor_xpds
%{_mandir}/man8/dahdi_cfg.8.*
%{_mandir}/man8/dahdi_genconf.8.*
%{_mandir}/man8/dahdi_hardware.8.*
%{_mandir}/man8/dahdi_monitor.8.*
%{_mandir}/man8/dahdi_registration.8.*
%{_mandir}/man8/dahdi_scan.8.*
%{_mandir}/man8/dahdi_test.8.*
%{_mandir}/man8/dahdi_tool.8.*
%{_mandir}/man8/fpga_load.8.*
%{_mandir}/man8/fxotune.8.*
%{_mandir}/man8/lsdahdi.8.*
%{_mandir}/man8/xpp_blink.8.*
%{_mandir}/man8/xpp_sync.8.*

%files -n %{libname}
%defattr(-,root,root)
%doc ChangeLog README LICENSE LICENSE.LGPL
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%dir %{_includedir}/dahdi
%{_includedir}/dahdi/*.h
%{_libdir}/*.so

%files -n perl-Dahdi
%defattr(-,root,root)
%{perl_vendorlib}/Dahdi
%{perl_vendorlib}/Dahdi.pm

%files -n dkms-dahdi
%defattr(-,root,root)
%doc dahdi-linux-%{linux_version}/ChangeLog
%doc dahdi-linux-%{linux_version}/LICENSE*
%doc dahdi-linux-%{linux_version}/README*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/40-dahdi.rules
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/40-xpp.rules
/lib/firmware/dahdi*
/lib/firmware/.dahdi*
%{_datadir}/dahdi/FPGA_1141.hex
%{_datadir}/dahdi/FPGA_1151.hex
%{_datadir}/dahdi/FPGA_FXS.hex
%{_datadir}/dahdi/USB_FW.hex
%{_datadir}/dahdi/XppConfig.pm
%{_datadir}/dahdi/init_card_1_30
%{_datadir}/dahdi/init_card_2_30
%{_datadir}/dahdi/init_card_3_30
%{_datadir}/dahdi/init_card_4_30
/usr/src/dahdi-%{linux_version}-%{release}
