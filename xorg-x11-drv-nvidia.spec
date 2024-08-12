%global        _nvidia_serie        nvidia
# Unfortunately this is always hardcoded regardless of architecture:
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2443
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2556-L2558
%global        _alternate_dir       %{_prefix}/lib/nvidia

%global        _dbus_systemd_dir    %{_datadir}/dbus-1/system.d
%global        _dracut_conf_d       %{_prefix}/lib/dracut/dracut.conf.d
%global        _grubby              %{_sbindir}/grubby --update-kernel=ALL
%global        _firmwarepath        %{_prefix}/lib/firmware
%global        _winedir             %{_libdir}/nvidia/wine
%global        _dracutopts          rd.driver.blacklist=nouveau modprobe.blacklist=nouveau
%if 0%{?rhel}
%global        _systemd_util_dir    %{_prefix}/lib/systemd
%endif

%global        debug_package %{nil}
%global        __strip /bin/true
%global        __brp_ldconfig %{nil}
%undefine      _missing_build_ids_terminate_build

Name:            xorg-x11-drv-nvidia
Epoch:           3
Version:         560.31.02
Release:         2%{?dist}
Summary:         NVIDIA's proprietary display driver for NVIDIA graphic cards

License:         Redistributable, no modification permitted
URL:             https://www.nvidia.com/
Source0:         https://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source1:         https://download.nvidia.com/XFree86/Linux-aarch64/%{version}/NVIDIA-Linux-aarch64-%{version}.run
Source5:         alternate-install-present
Source6:         nvidia.conf
Source7:         80-nvidia-pm.rules
Source8:         xorg-x11-drv-nvidia.metainfo.xml
Source9:         parse-supported-gpus.py
Source11:        nvidia-uvm.conf
Source12:        99-nvidia-dracut.conf
Source13:        10-nvidia.rules
Source14:        nvidia-fallback.service
Source15:        rhel_nvidia.conf
Source16:        nvidia-power-management.conf
Source17:        70-nvidia.preset

ExclusiveArch: x86_64 i686 aarch64

# Xorg with PrimaryGPU
Requires:         Xorg >= 1.19.0-3

Requires(post):   ldconfig
Requires(postun): ldconfig
Requires(post):   /usr/sbin/grubby
Requires:         which
Requires:         nvidia-settings%{?_isa} = %{?epoch}:%{version}
Requires:         nvidia-modprobe%{?_isa} = %{?epoch}:%{version}
BuildRequires:    systemd-rpm-macros
# AppStream metadata generation
BuildRequires:    python3
BuildRequires:    libappstream-glib >= 0.6.3
# Needed so nvidia-settings can write broken configs
Suggests:         nvidia-xconfig%{?_isa} = %{?epoch}:%{version}
# nvidia-bug-report.sh requires needed to provide extra info
Suggests:         acpica-tools
Suggests:         vulkan-tools
%ifarch x86_64
Recommends:       %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Recommends:       %{name}-power%{?_isa} = %{?epoch}:%{version}-%{release}
%endif

Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}

Obsoletes:       %{_nvidia_serie}-kmod < %{?epoch}:%{version}
Provides:        %{_nvidia_serie}-kmod-common = %{?epoch}:%{version}
# Support nvidia-open-kmod
Provides:        %{_nvidia_serie}-open-kmod-common = %{?epoch}:%{version}
Conflicts:       xorg-x11-drv-nvidia-340xx
Conflicts:       xorg-x11-drv-nvidia-390xx

%global         __provides_exclude ^(lib.*GL.*\\.so.*)$
%global         __requires_exclude ^libglxserver_nvidia.so|^(lib.*GL.*\\.so.*)$


%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with current NVIDIA chipsets series.
Fermi and Kelper GPUs NOT supported by this release.

For the full product support list, please consult the release notes
http://download.nvidia.com/XFree86/Linux-x86_64/%{version}/README/index.html

Please use the following documentation:
http://rpmfusion.org/Howto/NVIDIA


%package devel
Summary:         Development files for %{name}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}

#Don't put an epoch here
Provides:        cuda-drivers-devel = %{version}.100
Provides:        cuda-drivers-devel%{?_isa} = %{version}.100
Provides:        nvidia-driver-devel = %{?epoch}:%{version}-100
Provides:        nvidia-driver-devel%{?_isa} = %{?epoch}:%{version}-100
Provides:        nvidia-drivers-devel = %{?epoch}:%{version}-100
Provides:        nvidia-drivers-devel%{?_isa} = %{?epoch}:%{version}-100

%description devel
This package provides the development files of the %{name} package.

%package cuda
Summary:         CUDA driver for %{name}
Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:        nvidia-persistenced%{?_isa} = %{?epoch}:%{version}
Requires:        nvidia-modprobe%{?_isa} = %{?epoch}:%{version}
%ifarch x86_64
Requires:        (%{name}-cuda-libs(x86-32) = %{?epoch}:%{version}-%{release} if mesa-libGL(x86-32))
%endif
Requires:        ocl-icd%{?_isa}
Requires:        opencl-filesystem

Conflicts:       xorg-x11-drv-nvidia-340xx-cuda

#Don't put an epoch here
Provides:        cuda-drivers-%(echo %{version} | cut -f 1 -d .) = %{version}
Provides:        cuda-drivers = %{version}.100
Provides:        cuda-drivers%{?_isa} = %{version}.100
Obsoletes:       cuda-drivers < %{version}.100
Provides:        nvidia-driver = %{?epoch}:%{version}-100
Provides:        nvidia-driver%{?_isa} = %{?epoch}:%{version}-100
Provides:        nvidia-drivers = %{?epoch}:%{version}-100
Provides:        nvidia-drivers%{?_isa} = %{?epoch}:%{version}-100
Provides:        nvidia-open = %{?epoch}:%{version}-100
Provides:        nvidia-open%{?_isa} = %{?epoch}:%{version}-100

%description cuda
This package provides the CUDA driver.

%package cuda-libs
Summary:         CUDA libraries for %{name}

%description cuda-libs
This package provides the CUDA driver libraries.

%package kmodsrc
Summary:         %{name} kernel module source code

%description kmodsrc
Source tree used for building kernel module packages (%{name}-kmod)
which is generated during the build of main package.

%package libs
Summary:         Libraries for %{name}
Requires:        libvdpau%{?_isa} >= 0.5
Requires:        libglvnd-egl%{?_isa} >= 0.2
Requires:        libglvnd-gles%{?_isa} >= 0.2
Requires:        libglvnd-glx%{?_isa} >= 0.2
Requires:        libglvnd-opengl%{?_isa} >= 0.2
Requires:        vulkan-loader%{?_isa}

Obsoletes:       egl-wayland < 1.1.15
Obsoletes:       egl-gbm < 2:1.1.2

# Boolean dependencies are only fedora and el8
%ifarch x86_64
Requires:        (%{name}-libs(x86-32) = %{?epoch}:%{version}-%{release} if mesa-libGL(x86-32))
%endif
Requires:        mesa-libEGL%{?_isa}
Requires:        mesa-libGL%{?_isa}
Requires:        mesa-libGLES%{?_isa}


%description libs
This package provides the shared libraries for %{name}.

%package power
Summary:          Advanced  power management
Requires:         %{name}%{?_isa} = %{?epoch}:%{version}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
# Mash can't handle noach package
#BuildArch:        noarch

%description power
Advanced  power management, preserve memory allocation on suspend/resume.

%prep
%setup -q -c -T
%ifarch i686 x86_64
sh %{SOURCE0} \
  --extract-only --target nvidiapkg
%else
%ifarch aarch64
sh %{SOURCE1} \
  --extract-only --target nvidiapkg
%endif
%endif

%build
# Nothing to build
echo "Nothing to build"


%install
cd nvidiapkg

# Install only required libraries
mkdir -p %{buildroot}%{_libdir}
%ifarch i686
pushd 32
%endif
cp -a \
    libcuda.so.%{version} \
    libEGL_nvidia.so.%{version} \
    libGLESv1_CM_nvidia.so.%{version} \
    libGLESv2_nvidia.so.%{version} \
    libGLX_nvidia.so.%{version} \
    libnvcuvid.so.%{version} \
    libnvidia-allocator.so.%{version} \
    libnvidia-eglcore.so.%{version} \
    libnvidia-egl-gbm.so.1.1.1 \
    libnvidia-egl-wayland.so.1.1.13 \
    libnvidia-egl-xcb.so.1 \
    libnvidia-egl-xlib.so.1 \
    libnvidia-encode.so.%{version} \
    libnvidia-fbc.so.%{version} \
    libnvidia-glcore.so.%{version} \
    libnvidia-glsi.so.%{version} \
    libnvidia-glvkspirv.so.%{version} \
    libnvidia-gpucomp.so.%{version} \
    libnvidia-ml.so.%{version} \
    libnvidia-nvvm.so.%{version} \
    libnvidia-opticalflow.so.%{version} \
    libnvidia-ptxjitcompiler.so.%{version} \
%ifarch x86_64 aarch64
    libcudadebugger.so.%{version} \
    libnvidia-api.so.1 \
    libnvidia-cfg.so.%{version} \
    libnvidia-ngx.so.%{version} \
%ifnarch aarch64
    libnvidia-vksc-core.so.%{version} \
%if 0%{?fedora} || 0%{?rhel} > 8
    libnvidia-pkcs11-openssl3.so.%{version} \
%else
    libnvidia-pkcs11.so.%{version} \
%endif
%endif
    libnvidia-rtcore.so.%{version} \
    libnvoptix.so.%{version} \
%endif
    %{buildroot}%{_libdir}/

cp -af \
    libnvidia-opencl.so.%{version} \
    libnvidia-tls.so.%{version} \
    %{buildroot}%{_libdir}/

# Use ldconfig for libraries with a mismatching SONAME/filename
ldconfig -vn %{buildroot}%{_libdir}/

# Libraries you can link against
for lib in libcuda libnvcuvid libnvidia-encode libnvidia-ml libnvidia-nvvm; do
    ln -sf $lib.so.%{version} %{buildroot}%{_libdir}/$lib.so
done

# Vdpau driver
install -D -p -m 0755 libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
ln -sf libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.1

# GBM symlink
install    -m 0755         -d %{buildroot}%{_libdir}/gbm/
ln -sf ../libnvidia-allocator.so.%{version} %{buildroot}%{_libdir}/gbm/nvidia-drm_gbm.so

%ifarch i686
popd
%endif

%ifarch x86_64 aarch64
# Vulkan config and symlink
install    -m 0755         -d %{buildroot}%{_datadir}/vulkan/{icd.d,implicit_layer.d}/
install -p -m 0644 nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/
install -p -m 0644 nvidia_layers.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/

# X DDX driver and GLX extension
install -p -D -m 0755 libglxserver_nvidia.so.%{version} %{buildroot}%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
install -D -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so

# OpenCL config
install    -m 0755         -d %{buildroot}%{_sysconfdir}/OpenCL/vendors/
install -p -m 0644 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/

# EGL config for libglvnd
install    -m 0755         -d %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
install -p -m 0644 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# EGL configs
install -m 0755 -d %{buildroot}%{_datadir}/egl/egl_external_platform.d/
install -pm 0644 10_nvidia_wayland.json 15_nvidia_gbm.json 20_nvidia_xcb.json 20_nvidia_xlib.json \
 %{buildroot}%{_datadir}/egl/egl_external_platform.d/

# Blacklist nouveau, autoload nvidia-uvm module after nvidia module
mkdir -p %{buildroot}%{_modprobedir}
install -p -m 0644 %{SOURCE11} %{buildroot}%{_modprobedir}
install -p -m 0644 %{SOURCE16} %{buildroot}%{_modprobedir}

%ifarch x86_64
# Install VulkanSC config
install    -m 0755 -d               %{buildroot}%{_datadir}/vulkansc/icd.d/
install -p -m 0644 nvidia_icd_vksc.json %{buildroot}%{_datadir}/vulkansc/icd.d/
# Install dbus config
install    -m 0755 -d               %{buildroot}%{_dbus_systemd_dir}
install -p -m 0644 nvidia-dbus.conf %{buildroot}%{_dbus_systemd_dir}
%endif

# dracut.conf.d file, nvidia modules must never be in the initrd
install -p -m 0755 -d          %{buildroot}%{_dracut_conf_d}/
install -p -m 0644 %{SOURCE12} %{buildroot}%{_dracut_conf_d}/

# Install binaries
install -m 0755 -d %{buildroot}%{_bindir}
install -p -m 0755 nvidia-{bug-report.sh,debugdump,smi,cuda-mps-control,cuda-mps-server,ngx-updater} \
  %{buildroot}%{_bindir}
%ifarch x86_64
install -p -m 0755 nvidia-powerd nvidia-pcc \
  %{buildroot}%{_bindir}
%endif

# Install man pages
install    -m 0755 -d   %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{cuda-mps-control,smi}.1.gz \
  %{buildroot}%{_mandir}/man1/

#Alternate-install-present is checked by the nvidia .run
mkdir -p %{buildroot}%{_alternate_dir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_alternate_dir}

#install the NVIDIA supplied application profiles
mkdir -p %{buildroot}%{_datadir}/nvidia
install -p -m 0644 nvidia-application-profiles-%{version}-{rc,key-documentation} %{buildroot}%{_datadir}/nvidia
install -p -m 0644 nvoptix.bin %{buildroot}%{_datadir}/nvidia
ln -s nvidia-application-profiles-%{version}-rc %{buildroot}%{_datadir}/nvidia/nvidia-application-profiles-rc
ln -s nvidia-application-profiles-%{version}-key-documentation %{buildroot}%{_datadir}/nvidia/nvidia-application-profiles-key-documentation

#Install the Xorg configuration files
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d
%if 0%{?fedora}
install -pm 0644 %{SOURCE6} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
%else
install -pm 0644 %{SOURCE15} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
%endif

#Ghost Xorg nvidia.conf files
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/nvidia.conf

#Create the default nvidia config directory
mkdir -p %{buildroot}%{_sysconfdir}/nvidia

#Install the nvidia kernel modules sources archive
mkdir -p %{buildroot}%{_datadir}/nvidia-kmod-%{version}
tar Jcf %{buildroot}%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_arch}.tar.xz kernel kernel-open
%ifarch x86_64
#Install wine dll
mkdir -p %{buildroot}%{_winedir}
install -p -m 0644 _nvngx.dll nvngx.dll %{buildroot}%{_winedir}
%endif

#RPM Macros support
mkdir -p %{buildroot}%{rpmmacrodir}
cat > %{buildroot}%{rpmmacrodir}/macros.%{name}-kmodsrc<< EOF
# nvidia_kmodsrc_version RPM Macro
%nvidia_kmodsrc_version	%{version}
EOF

# install AppData and add modalias provides
install -D -p -m 0644 %{SOURCE8} %{buildroot}%{_metainfodir}/xorg-x11-drv-nvidia.metainfo.xml
%{SOURCE9} supported-gpus/supported-gpus.json | xargs appstream-util add-provide %{buildroot}%{_metainfodir}/xorg-x11-drv-nvidia.metainfo.xml modalias
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -pm 0644 nvidia-settings.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

# Install nvidia-fallback
install -m 0755 -d %{buildroot}%{_unitdir}
install -m 0755 -d %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE13} %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE14} %{buildroot}%{_unitdir}

# UDev rules for PCI-Express Runtime D3 (RTD3) Power Management
install -p -m 0644 %{SOURCE7} %{buildroot}%{_udevrulesdir}

# Systemd units and script for suspending/resuming
mkdir %{buildroot}%{_systemd_util_dir}/system-{sleep,preset}/
install -p -m 0644 %{SOURCE17} %{buildroot}%{_systemd_util_dir}/system-preset/
install -p -m 0644 systemd/system/nvidia-{hibernate,resume,suspend}.service %{buildroot}%{_unitdir}
%ifarch x86_64
install -p -m 0644 systemd/system/nvidia-powerd.service %{buildroot}%{_unitdir}
# Ignore powerd binary exiting if hardware is not present
# We should check for information in the DMI table
sed -i -e 's/ExecStart=/ExecStart=-/g' %{buildroot}%{_unitdir}/nvidia-powerd.service
%endif
install -p -m 0755 systemd/system-sleep/nvidia %{buildroot}%{_systemd_util_dir}/system-sleep/
install -p -m 0755 systemd/nvidia-sleep.sh %{buildroot}%{_bindir}

# Firmware
mkdir -p %{buildroot}%{_firmwarepath}/nvidia/%{version}/
install -p -m 0444 firmware/gsp_{ga,tu}10x.bin %{buildroot}%{_firmwarepath}/nvidia/%{version}/

%pre
if [ "$1" -eq "1" ]; then
  if [ -x %{_bindir}/nvidia-uninstall ]; then
    %{_bindir}/nvidia-uninstall -s && rm -f %{_bindir}/nvidia-uninstall &>/dev/null || :
  fi
fi

%post
if [ "$1" -eq "1" ]; then
  %{_grubby} --remove-args='nomodeset' --args='%{_dracutopts}' &>/dev/null
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
fi || :

%triggerun -- xorg-x11-drv-nvidia < 3:545.23.06-1
if [ -f %{_sysconfdir}/default/grub ] ; then
  sed -i -e '/GRUB_GFXPAYLOAD_LINUX=text/d' %{_sysconfdir}/default/grub
  . %{_sysconfdir}/default/grub
  if [ -z "${GRUB_CMDLINE_LINUX+x}" ]; then
    echo -e GRUB_CMDLINE_LINUX=\"%{_dracutopts}\" >> %{_sysconfdir}/default/grub
  else
    for i in %{_dracutopts} ; do
      _has_string=$(echo ${GRUB_CMDLINE_LINUX} | grep -F -c $i)
      if [ x"$_has_string" = x0 ] ; then
        GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} ${i}"
      fi
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
fi
%{_grubby} --args='%{_dracutopts}' &>/dev/null || :

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
  # Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && mv %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.nvidia_uninstalled &>/dev/null
fi ||:


%files
%license nvidiapkg/LICENSE
%doc nvidiapkg/NVIDIA_Changelog
%doc nvidiapkg/README.txt
%doc nvidiapkg/nvidia-application-profiles-%{version}-rc
%doc nvidiapkg/html
%ifarch x86_64
%{_bindir}/nvidia-pcc
%endif
%{_firmwarepath}
%dir %{_alternate_dir}
%{_alternate_dir}/alternate-install-present
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%{_datadir}/egl/egl_external_platform.d/*.json
%dir %{_sysconfdir}/nvidia
%ghost %{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/nvidia.conf
%{_datadir}/X11/xorg.conf.d/nvidia.conf
%{_udevrulesdir}/10-nvidia.rules
%{_udevrulesdir}/80-nvidia-pm.rules
%{_unitdir}/nvidia-fallback.service
%{_metainfodir}/%{name}.metainfo.xml
%{_datadir}/pixmaps/%{name}.png
%{_dracut_conf_d}/99-nvidia-dracut.conf
%{_bindir}/nvidia-bug-report.sh
# Xorg libs that do not need to be multilib
%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
#/no_multilib
%dir %{_datadir}/nvidia
%{_datadir}/nvidia/nvidia-application-profiles-*
%{_datadir}/nvidia/nvoptix.bin

%files kmodsrc
%dir %{_datadir}/nvidia-kmod-%{version}
%{rpmmacrodir}/macros.%{name}-kmodsrc
%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_arch}.tar.xz
%endif

%ldconfig_scriptlets libs
%files libs
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-allocator.so.1
%{_libdir}/libnvidia-allocator.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-egl-gbm.so.1
%{_libdir}/libnvidia-egl-gbm.so.1.1.1
%{_libdir}/libnvidia-egl-wayland.so.1
%{_libdir}/libnvidia-egl-wayland.so.1.1.13
%{_libdir}/libnvidia-egl-xcb.so.1
%{_libdir}/libnvidia-egl-xlib.so.1
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-glvkspirv.so.%{version}
%{_libdir}/libnvidia-gpucomp.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/gbm/
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%ifarch x86_64 aarch64
%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%{_datadir}/vulkan/icd.d/nvidia_icd.json
%{_libdir}/libnvidia-api.so.1
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%ifnarch aarch64
%if 0%{?fedora} || 0%{?rhel} > 8
%{_libdir}/libnvidia-pkcs11-openssl3.so.%{version}
%else
%{_libdir}/libnvidia-pkcs11.so.%{version}
%endif
%endif
%{_libdir}/libnvidia-ngx.so.1
%{_libdir}/libnvidia-ngx.so.%{version}
%{_libdir}/libnvidia-rtcore.so.%{version}
%{_libdir}/libnvoptix.so.1
%{_libdir}/libnvoptix.so.%{version}
%ifarch x86_64
%{_datadir}/vulkansc/icd.d/nvidia_icd_vksc.json
%{_libdir}/libnvidia-vksc-core.so.%{version}
%{_libdir}/libnvidia-vksc-core.so.1
%{_winedir}/
%endif
%endif

%ifarch x86_64 aarch64
%files cuda
%license nvidiapkg/LICENSE
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-ngx-updater
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
%endif

%ldconfig_scriptlets cuda-libs
%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-ml.so
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}
%{_libdir}/libnvidia-nvvm.so
%{_libdir}/libnvidia-nvvm.so.4
%{_libdir}/libnvidia-nvvm.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%{_libdir}/libnvidia-opticalflow.so.1
%{_libdir}/libnvidia-opticalflow.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.1
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%ifarch x86_64 aarch64
%{_libdir}/libcudadebugger.so.1
%{_libdir}/libcudadebugger.so.%{version}
%{_modprobedir}/nvidia-uvm.conf
%endif

%files devel

%ifarch x86_64 aarch64
%post power
%systemd_post nvidia-hibernate.service
%ifarch x86_64
%systemd_post nvidia-powerd.service
%endif
%systemd_post nvidia-resume.service
%systemd_post nvidia-suspend.service

%preun power
%systemd_preun nvidia-hibernate.service
%ifarch x86_64
%systemd_preun nvidia-powerd.service
%endif
%systemd_preun nvidia-resume.service
%systemd_preun nvidia-suspend.service

%postun power
%systemd_postun nvidia-hibernate.service
%ifarch x86_64
%systemd_postun nvidia-powerd.service
%endif
%systemd_postun nvidia-resume.service
%systemd_postun nvidia-suspend.service

%files power
%config %{_modprobedir}/nvidia-power-management.conf
%ifarch x86_64
%{_bindir}/nvidia-powerd
%{_unitdir}/nvidia-powerd.service
%{_dbus_systemd_dir}/nvidia-dbus.conf
%endif
%{_bindir}/nvidia-sleep.sh
%{_systemd_util_dir}/system-preset/70-nvidia.preset
%{_systemd_util_dir}/system-sleep/nvidia
%{_unitdir}/nvidia-hibernate.service
%{_unitdir}/nvidia-resume.service
%{_unitdir}/nvidia-suspend.service
%endif

%changelog
* Mon Aug 12 2024 Nicolas Chauvet <kwizart@gmail.com> - 3:560.31.02-2
- Provides nvidia-open for cuda-12-6

* Tue Aug 06 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.31.02-1
- Update to 560.31.02 beta

* Wed Jul 24 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.28.03-2
- Use bundled egl-wayland and egl-gbm

* Tue Jul 23 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.28.03-1
- Update to 560.28.03 beta

* Mon Jul 01 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.58.02-1
- Update to 555.58.02

* Thu Jun 27 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.58-1
- Update to 555.58 release

* Wed Jun 05 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.52.04-1
- Update to 555.52.04 beta

* Tue May 21 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.42.02-1
- Update to 555.42.02 beta

* Fri Apr 26 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.78-1
- Update to 550.78 release

* Wed Apr 17 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.76-1
- Update to 550.76 release

* Wed Mar 20 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.67-1
- Update to 550.67 release

* Fri Feb 23 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.54.14-1
- Update to 550.54.14 release

* Wed Jan 24 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.40.07-1
- Update to 550.40.07 beta

* Mon Dec 18 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.06-2
- Do not mark nvidia-powerd unit as failed if the binary exits

* Wed Nov 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.06-1
- Update to 545.29.06 release

* Fri Nov 03 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.02-4
- Readd nvidia power management udev rules

* Fri Nov 03 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.02-3
- Add requires nvidia-modprobe to main package

* Fri Nov 03 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.02-2
- Use nvidia-modprobe instead of udev rules (rfbz#6784)

* Tue Oct 31 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.02-1
- Update to 545.29.02 release

* Tue Oct 17 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.23.06-1
- Update to 545.23.06 beta
- Remove  nvidia-drm.modeset from boot options

* Fri Sep 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.113.01-1
- Update to 535.113.01

* Tue Aug 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.104.05-1
- Update to 535.104.05

* Mon Aug 14 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.98-2
- Add nvidia-drm.modeset=1 to cmdline

* Tue Aug 08 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.98-1
- Update to 535.98

* Tue Jul 18 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.86.05-1
- Update to 535.86.05

* Thu Jun 15 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.54.03-2
- Install firmware signature
- Use openssl3 for fedora and el9

* Wed Jun 14 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.54.03-1
- Update to 535.54.03

* Tue May 30 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.43.02-1
- Update to 535.43.02 beta

* Thu Mar 23 2023 Leigh Scott <leigh123linux@gmail.com> - 3:530.41.03-1
- Update to 530.41.03

* Tue Mar 07 2023 Leigh Scott <leigh123linux@gmail.com> - 3:530.30.02-2
- Remove modeset cmd option as it been default enabled in the kmod

* Sat Mar 04 2023 Leigh Scott <leigh123linux@gmail.com> - 3:530.30.02-1
- Update to 530.30.02 beta

* Thu Feb 09 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.89.02-1
- Update to 525.89.02

* Thu Jan 19 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.85.05-1
- Update to 525.85.05

* Thu Jan 05 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.78.01-1
- Update to 525.78.01

* Mon Nov 28 2022 Leigh Scott <leigh123linux@gmail.com> - 3:525.60.11-1
- Update to 525.60.11

* Thu Nov 10 2022 Leigh Scott <leigh123linux@gmail.com> - 3:525.53-1
- Update to 525.53 beta

* Wed Oct 12 2022 Leigh Scott <leigh123linux@gmail.com> - 3:520.56.06-1
- Update to 520.56.06

* Sun Sep 25 2022 Dennis Gilmore <dennis@ausil.us> - 3:515.76-2
- add initial aarch64 support

* Wed Sep 21 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.76-1
- Update to 515.76

* Fri Aug 12 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:515.65.01-2
- Add support for nvidia-open-kmod

* Thu Aug 04 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.65.01-1
- Update to 515.65.01

* Tue Jun 28 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.57-1
- Update to 515.57

* Tue May 31 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:515.48.07-1
- Update to 515.48.07

* Thu May 26 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.43.04-5
- Add option to blacklist simpledrm

* Sun May 15 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:515.43.04-4
- Add both kernel and kernel-open to the kmodsrc

* Thu May 12 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.43.04-3
- kernel-open isn't ready for main stream use

* Thu May 12 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.43.04-2
- Remove nvidia-settings lib

* Wed May 11 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.43.04-1
- Update to 515.43.04 beta

* Tue Apr 26 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:510.68.02-1
- Update to 510.68.02

* Wed Mar 23 2022 Leigh Scott <leigh123linux@gmail.com> - 3:510.60.02-1
- Update to 510.60.02 release

* Mon Feb 14 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:510.54-1
- Update to 510.54

* Tue Feb 01 2022 Leigh Scott <leigh123linux@gmail.com> - 3:510.47.03-1
- Update to 510.47.03 release

* Fri Jan 21 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:510.39.01-2
- Add dbus-nvidia.conf

* Tue Jan 11 2022 Leigh Scott <leigh123linux@gmail.com> - 3:510.39.01-1
- Update to 510.39.01 beta

* Tue Dec 14 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.46-1
- Update to 495.46 release

* Tue Nov 02 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.44-4
- Fix appdata

* Mon Nov 01 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.44-3
- Add libnvidia-vulkan-producer symlink

* Thu Oct 28 2021 Nicolas Chauvet <kwizart@gmail.com> - 3:495.44-2
- Update egl-wayland deps
- Drop mesa version enforcing

* Tue Oct 26 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.44-1
- Update to 495.44 release

* Sat Oct 16 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.29.05-4
- 15_nvidia_gbm.json moved to egl-wayland

* Sat Oct 16 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.29.05-3
- Fix symlink directory for nvidia-drm_gbm.so
- Increase egl-wayland requires to 1.1.9

* Thu Oct 14 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.29.05-2
- Add nvidia-drm_gbm.so symlink

* Thu Oct 14 2021 Leigh Scott <leigh123linux@gmail.com> - 3:495.29.05-1
- Update to 495.29.05 beta

* Mon Sep 20 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.74-1
- Update to 470.74 release

* Tue Aug 24 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.63.01-3
- Mash can't handle noach package

* Mon Aug 23 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.63.01-2
- Move power management files to sub-package

* Tue Aug 10 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.63.01-1
- Update to 470.63.01 release

* Tue Jul 20 2021 Olivier Fourdan <fourdan@gmail.com> - 3:470.57.02-2
- Add power management option (NVreg_PreserveVideoMemoryAllocations)

* Mon Jul 19 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.57.02-1
- Update to 470.57.02 release

* Tue Jul 06 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.42.01-2
- Install dll to correct directory

* Tue Jun 22 2021 Leigh Scott <leigh123linux@gmail.com> - 3:470.42.01-1
- Update to 470.42.01 beta

* Fri May 21 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.31-1
- Update to 465.31 release

* Thu Apr 29 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.27-1
- Update to 465.27 release

* Wed Apr 21 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.24.02-4
- Fix firmware directory ownership

* Wed Apr 21 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.24.02-3
- Fix firmware path

* Thu Apr 15 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.24.02-2
- Update AppStream metadata generation

* Wed Apr 14 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.24.02-1
- Update to 465.24.02 release

* Tue Mar 30 2021 Leigh Scott <leigh123linux@gmail.com> - 3:465.19.01-1
- Update to 465.19.01 beta

* Fri Mar 19 2021 Leigh Scott <leigh123linux@gmail.com> - 3:460.67-1
- Update to 460.67 release

* Tue Mar 16 2021 Nicolas Chauvet <kwizart@gmail.com> - 3:460.56-3
- Revert previous commit

* Fri Mar 12 2021 Nicolas Chauvet <kwizart@gmail.com> - 3:460.56-2
- Adjust virtual provides

* Thu Feb 25 2021 Leigh Scott <leigh123linux@gmail.com> - 3:460.56-1
- Update to 460.56 release

* Tue Jan 26 2021 Leigh Scott <leigh123linux@gmail.com> - 3:460.39-1
- Update to 460.39 release

* Thu Jan  7 2021 Leigh Scott <leigh123linux@gmail.com> - 3:460.32.03-1
- Update to 460.32.03 release

* Sat Dec 19 2020 Leigh Scott <leigh123linux@gmail.com> - 3:460.27.04-2
- Add missed bin files

* Wed Dec 16 2020 Leigh Scott <leigh123linux@gmail.com> - 3:460.27.04-1
- Update to 460.27.04 beta

* Wed Nov 18 2020 Leigh Scott <leigh123linux@gmail.com> - 3:455.45.01-1
- Update to 455.45.01 release

* Thu Oct 29 2020 Leigh Scott <leigh123linux@gmail.com> - 3:455.38-1
- Update to 455.38 release

* Wed Oct  7 2020 Leigh Scott <leigh123linux@gmail.com> - 3:455.28-1
- Update to 455.28 release

* Thu Sep 17 2020 Leigh Scott <leigh123linux@gmail.com> - 3:455.23.04-1
- Update to 455.23.04 beta

* Fri Aug 28 2020 Leigh Scott <leigh123linux@gmail.com> - 3:450.66-2
- Install the systemd power management files

* Tue Aug 18 2020 Leigh Scott <leigh123linux@gmail.com> - 3:450.66-1
- Update to 450.66 release

* Thu Jul 09 2020 Leigh Scott <leigh123linux@gmail.com> - 3:450.57-1
- Update to 450.57 release

* Wed Jun 24 2020 Leigh Scott <leigh123linux@gmail.com> - 3:450.51-1
- Update to 450.51 beta

* Tue Apr 07 2020 leigh123linux <leigh123linux@googlemail.com> - 3:440.82-2
- Update to 440.82 release

* Wed Mar 11 2020 Nicolas Chauvet <kwizart@gmail.com> - 3:440.64-2
- Deal with cuda-drivers insanity

* Fri Feb 28 2020 leigh123linux <leigh123linux@googlemail.com> - 3:440.64-1
- Update to 440.64 release

* Tue Feb 25 2020 Leigh Scott <leigh123linux@googlemail.com> - 3:440.59-3
- Remove 'Disable wayland if gdm is available', gdm has it's own blacklist

* Sat Feb 15 2020 Leigh Scott <leigh123linux@googlemail.com> - 3:440.59-2
- Ensure that only one Vulkan ICD manifest is present

* Mon Feb 03 2020 Leigh Scott <leigh123linux@gmail.com> - 3:440.59-1
- Update to 440.59 release

* Mon Dec 16 2019 Leigh Scott <leigh123linux@googlemail.com>
- Fix boolean requires on libs

* Wed Dec 11 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:440.44-1
- Update to 440.44 release

* Fri Nov 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:440.36-1
- Update to 440.36 release

* Mon Nov 04 2019 Leigh Scott <leigh123linux@gmail.com> - 3:440.31-1
- Update to 440.31 release

* Thu Oct 17 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:440.26-1
- Update to 440.26 beta

* Thu Sep 19 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:435.21-2
- Fix conflict with rpmfusion-nonfree-obsolete-packages

* Thu Aug 29 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:435.21-1
- Update to 435.21 release

* Sat Aug 24 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:435.17-4
- Add Vulkan layer for Optimus
- Add Suggests acpica-tools and vulkan-tools (nvidia-bug-report.sh)

* Wed Aug 21 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:435.17-3
- Switch to python3 for appdata

* Tue Aug 20 2019 Nicolas Chauvet <kwizart@gmail.com> - 3:435.17-2
- Use AllowNVIDIAGPUScreens for Optimus offload sync support
- Disable PrimaryGPU by default

* Tue Aug 13 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:435.17-1
- Update to 435.17 beta

* Mon Jul 29 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:430.40-1
- Update to 430.40 release

* Mon Jul 15 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:430.34-1
- Update to 430.34 release

* Tue Jun 11 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:430.26-1
- Update to 430.26 release

* Tue May 14 2019 Leigh Scott <leigh123linux@gmail.com> - 3:430.14-1
- Update to 430.14 release

* Wed Apr 24 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:430.09-1
- Update to 430.09 beta

* Thu Mar 21 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:418.56-1
- Update to 418.56 release

* Fri Feb 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:418.43-1
- Update to 418.43 release

* Sat Feb 02 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:418.30-1
- Update to 418.30 beta

* Wed Jan 16 2019 Leigh Scott <leigh123linux@googlemail.com> - 3:415.27-1
- Update to 415.27 release

* Wed Dec 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.25-2
- Bump for el7 multi-lib build

* Wed Dec 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.25-1
- Update to 415.25 release

* Fri Dec 14 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.23-1
- Update to 415.23 release

* Mon Dec 10 2018 Nicolas Chauvet <kwizart@gmail.com> - 3:415.22-4
- Add nvidia_kmodsrc_version macro

* Sat Dec 08 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.22-3
- Move nvidia-uvm.conf and 60-nvidia-uvm.rules to cuda-libs,
  nvdec shouldn't need the cuda package to function.

* Fri Dec 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.22-2
- Update to 415.22 release
- Fix some rpmlint warnings

* Wed Nov 21 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:415.18-1
- Update to 415.18 release

* Fri Nov 16 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.78-1
- Update to 410.78 release

* Sun Nov 11 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.73-2
- Use different output class for rhel as it chokes on options

* Thu Oct 25 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.73-1
- Update to 410.73 release

* Tue Oct 16 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.66-1
- Update to 410.66 release

* Wed Oct 10 2018 Nicolas Chauvet <kwizart@gmail.com> - 3:410.57-6
- Enforce the mesa version

* Sat Sep 29 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.57-5
- Add epoch to nvidia-modprobe and nvidia-xconfig requires

* Sun Sep 23 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.57-4
- Add new raytracing libs
- Move the new glx server lib to it's correct location

* Fri Sep 21 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.57-3
- Add epoch to nvidia-settings requires

* Thu Sep 20 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.57-2
- Filter libglxserver_nvidia.so requires on main

* Thu Sep 20 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:410.57-1
- Update to 410.57 beta

* Wed Aug 29 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.54-3
- Rebase for RHEL-7.6 beta

* Wed Aug 22 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.54-2
- Add epoch to for nvidia-persistenced requires

* Wed Aug 22 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.54-1
- Update to 396.54 release

* Sat Aug 04 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.51-1
- Update to 396.51 release
- Change vulkan requires

* Fri Jul 20 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.45-1
- Update to 396.45 release
- Add compat provide for cuda repo

* Fri Jun 22 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.24-3
- Readd devel sub-package for i686

* Fri May 04 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.24-2
- Clean up

* Fri May 04 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:396.24-1
- Update to 396.24 release

* Mon Apr 09 2018 Nicolas Chauvet <kwizart@gmail.com> - 3:390.48-2
- Add icon to be used by appdata
- Add cuda-libs(x86-32) if libGL(x86-32) is present
- Remove any desktop file from the driver

* Wed Mar 28 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:390.48-1
- Update to 390.48 release

* Mon Mar 19 2018 Nicolas Chauvet <kwizart@gmail.com> - 3:390.42-2
- Disable since we rely on OutputClass here
- Use PrimaryGPU feature since Xorg >= 1.19
- Use ldconfig_scriptlets macro
- Disable uneeded ldconfig call from main
- Disable wayland if gdm is available - See rhbz#1462052
- Fixup removed f24 support
- Fixup urls

* Tue Mar 13 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:390.42-1
- Update to 390.42 release

* Fri Mar 02 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 3:390.25-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 16 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:390.25-4
- mesa-libGL provides libGLX_indirect.so.0 on fedora

* Thu Feb 15 2018 Leigh Scott <leigh123linux@googlemail.com> - 3:390.25-3
- Bump epoch to prevent cuda repo from replacing -kmodsrc

* Fri Feb 02 2018 Leigh Scott <leigh123linux@googlemail.com> - 2:390.25-2
- Fix omitting drivers from the initrd.

* Mon Jan 29 2018 Leigh Scott <leigh123linux@googlemail.com> - 2:390.25-1
- Update to 390.25 release

* Wed Jan 10 2018 Leigh Scott <leigh123linux@googlemail.com> - 2:390.12-1
- Update to 390.12 beta

* Sat Dec 16 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:387.34-2
- Add plymouth advertising for nvidia-fallback.service

* Sun Nov 26 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:387.34-1
- Update to 387.34 release

* Sun Nov 05 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:387.22-3
- Remove nomodeset from cmdline during install

* Tue Oct 31 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:387.22-2
- Remove the prebuilt tools and use rpm packages instead

* Mon Oct 30 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:387.22-1
- Update to 387.22 release

* Wed Oct 04 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:387.12-1
- Update to 387.12 beta

* Thu Sep 21 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:384.90-1
- Update to 384.90 release

* Thu Aug 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:384.59-5
- Enable modeset by default for F27+
- Ensure the correct selinux context it set

* Wed Aug 16 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:384.59-4
- Use kernel option instead to set modeset for DRM module

* Tue Aug 15 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:384.59-3
- Add udev rules so nvidia nodes are created under EGLDevice/wayland
- Enable modeset for DRM

* Fri Aug 04 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:384.59-2
- Add nvidia-fallback support

* Tue Jul 25 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:384.59-1
- Update to 384.59 release

* Mon Jul 24 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:375.82-1
- Update to 375.82 release
- Fix non-glvnd build

* Mon Jul 10 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-9
- Fixup for non-glvnd vulkan loader

* Wed Jul 05 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-8
- Make libglvnd optional on rhel
- Use boolean dependency on fedora 25 also

* Tue Jun 13 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-7
- Use | instead of / for sed GRUB_CMDLINE_LINUX

* Fri Jun 02 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-6
- Remove GRUB_GFXPAYLOAD_LINUX from default/grub

* Tue May 30 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-5
- Update the triggerin to insert the new cmdline
- Avoid the nvidia modules to get added to the initramfs - patch by hansg

* Tue May 30 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:375.66-3
- Revert 10_nvidia.json rename

* Fri May 12 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-2
- Add epoch for triggerin

* Fri May 05 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:375.66-1
- Update to 375.66 release

* Wed Apr 26 2017 Nicolas Chauvet <kwizart@gmail.com> - 1:381.09-5
- Use modprobe.blacklist cmdline instead of blacklist file on fedora.
- Use triggerin to install the new cmdline
- Re-org Xorg config files installation
- Switch to http instead of ftp for download URL
- Point libGLX_indirect to Mesa on f25+ or to nvidia

* Mon Apr 10 2017 Simone Caronni <negativo17@gmail.com> - 1:381.09-3
- Also use split libglvnd packages for Fedora 24 and RHEL 6/7.

* Mon Apr 10 2017 Simone Caronni <negativo17@gmail.com> - 1:381.09-2
- Simplify GRUB installation for Grub 1 (RHEL 6) and Grub 2 (RHEL 7+/Fedora), do
  not use obsolete kernel parameters.
- Add kernel parameters to default grub file on Fedora/RHEL 7+.
- Bring default RHEL 6 X.org configuration on par with Fedora/RHEL 7+ and make
  sure it is installed by default.
- Install RHEL 6 X.org configuration template only on RHEL 6, make sure it does
  not end in .conf to avoid confusion.
- Package only required symlinks for libraries.
- Add only the libraries that program can link to in the devel subpackage.
- Make CUDA subpackages multilib compliant (no more CUDA i686 binaries on
  x86_64).
- Do not require main packages for libraries subpackages, this makes possible to
  build things that link to Nvidia drivers using only libraries and not pulling
  all the graphic driver components.
- Fix files listed twice during build.
- Install non conflicting libraries in standard locations, remove all redundant
  directory overrides for the various distributions. This also removes the link
  libGLX_indirect.so.0.
- Explicitly list all libraries included in the packages, avoid too many
  if/exclude directives.
- Various fixups from Nicolas Chauvet:
  * buildroot
  * glvnd vulkan to use _datadir
  * Use nvidia_libdir for alternate install file
  * arm and opencl

* Fri Apr 07 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:381.09-1
- Update to 381.09 beta

* Tue Mar 14 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:378.13-2
- Link libGLX_indirect.so.0 to libGLX_mesa.so.0

* Fri Mar 03 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:378.13-1
- Update to 378.13 release

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-7
- Use gtk 2 nvidia-settings library only on RHEL 6 and Fedora ARM.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-6
- Require source built libnvidia-egl-wayland library.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-5
- Use only newer ELF TLS implementation, supported since kernel 2.3.99 (pre RHEL
  4).

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-4
- Remove OpenCL loader, RPM filters and ownership of loader configuration.
- Require OpenCL filesystem and loader library.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-3
- Replace SUID nvidia-modprobe binary with configuration. Make sure the
  nvidia-uvm module is loaded when the CUDA subpackage is installed and that
  dracut does not try to pull in the module in the initrd.
- Remove leftovers from old distributions.
- Remove prelink configuration.
- Make sure the license is installed both with the base driver package and with
  the CUDA package.
- Make sure the package also builds and install on RHEL 6.
- Enable SLI and BaseMosaic by default on Fedora 25+.
- Trim changelog (<2015).

* Thu Feb 16 2017 Nicolas Chauvet <kwizart@gmail.com> - 1:375.39-2
- Avoid xorg dir symlink on fedora 25+
- Drop GFXPAYLOAD and video=vesa:off
- Implement cuda-libs (for steam)

* Tue Feb 14 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.39-1
- Update to 375.39 release

* Thu Jan 19 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-11
- Fix file conflict with filesystem

* Wed Jan 18 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-10
- Add conditions for el7 as there is no wayland

* Wed Jan 18 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-9
- Add conditions for f24 and el7

* Tue Jan 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-8
- Changes for mesa glvnd
- Move nvidia libs to lib directoy and remove ldconfig config file
- Add appdata info

* Sat Dec 31 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-7
- Update nvidia.conf for latest Xorg changes

* Sat Dec 24 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-6
- Fix error in nvidia.conf rfbz#4388

* Sat Dec 24 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-5
- Add xorg-x11-server-Xorg minimum version requires

* Mon Dec 19 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-4
- Add conditionals for f24

* Mon Dec 19 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-3
- Fix nvidia.conf

* Sun Dec 18 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-2
- Change conf files for Prime support

* Wed Dec 14 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-1
- Update to 375.26 release

* Fri Nov 18 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.20-1
- Update to 375.20 release

