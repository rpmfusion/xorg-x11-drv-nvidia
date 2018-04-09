%global        _nvidia_serie        nvidia
%global        _nvidia_libdir       %{_libdir}/%{_nvidia_serie}
%global        _nvidia_xorgdir      %{_nvidia_libdir}/xorg
# Unfortunately this is always hardcoded regardless of architecture:
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2443
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2556-L2558
%global        _alternate_dir       %{_prefix}/lib/nvidia
%global        _glvnd_libdir        %{_libdir}/libglvnd

%if 0%{?rhel} == 6
%global        _modprobe_d          %{_sysconfdir}/modprobe.d/
# RHEL 6 does not have _udevrulesdir defined
%global        _udevrulesdir        %{_prefix}/lib/udev/rules.d/
%global        _modprobe_d          %{_sysconfdir}/modprobe.d/
%global        _dracutopts          nouveau.modeset=0 rdblacklist=nouveau
%global        _dracut_conf_d	    %{_sysconfdir}/dracut.conf.d
%global        _grubby              /sbin/grubby --grub --update-kernel=ALL
%else #rhel > 6 or fedora
%global        _dracut_conf_d	    %{_prefix}/lib/dracut/dracut.conf.d
%global        _modprobe_d          %{_prefix}/lib/modprobe.d/
%global        _grubby              %{_sbindir}/grubby --update-kernel=ALL
%if 0%{?rhel} == 7
%global        _dracutopts          nouveau.modeset=0 rd.driver.blacklist=nouveau
%else #fedora
%if 0%{?fedora} >= 27
%global        _dracutopts          rd.driver.blacklist=nouveau modprobe.blacklist=nouveau nvidia-drm.modeset=1
%else
%global        _dracutopts          rd.driver.blacklist=nouveau modprobe.blacklist=nouveau
%endif
%endif
%endif

%global	       debug_package %{nil}
%global	       __strip /bin/true


Name:            xorg-x11-drv-nvidia
Epoch:           3
Version:         390.48
Release:         1%{?dist}
Summary:         NVIDIA's proprietary display driver for NVIDIA graphic cards

License:         Redistributable, no modification permitted
URL:             http://www.nvidia.com/
Source0:         https://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}.run
Source1:         https://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source2:         https://download.nvidia.com/XFree86/Linux-32bit-ARM/%{version}/NVIDIA-Linux-armv7l-gnueabihf-%{version}.run

Source4:         99-nvidia.conf
Source5:         00-avoid-glamor.conf
Source6:         blacklist-nouveau.conf
Source7:         alternate-install-present
Source10:        nvidia.conf
Source11:        60-nvidia.rules
Source12:        xorg-x11-drv-nvidia.metainfo.xml
Source13:        parse-readme.py
Source14:        60-nvidia-uvm.rules
Source15:        nvidia-uvm.conf
Source16:        99-nvidia-dracut.conf
Source20:        10-nvidia.rules
Source21:        nvidia-fallback.service

ExclusiveArch: i686 x86_64 armv7hl

%if 0%{?rhel} > 6 || 0%{?fedora}
Buildrequires:    systemd
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%endif
%if 0%{?fedora} >= 25
# AppStream metadata generation
BuildRequires:    python2
BuildRequires:    libappstream-glib >= 0.6.3
# Xorg with PrimaryGPU
Requires:         Xorg >= 1.19.0-3
%else
# Xorg with OutputClass
Requires:         Xorg >= 1.16.0-1
%endif

Requires(post):   ldconfig
Requires(postun): ldconfig
Requires(post):   grubby
Requires:         which
Requires:         nvidia-settings%{?_isa} = %{version}
%if 0%{?fedora}
Suggests:         nvidia-xconfig%{?_isa} = %{version}
%else
Requires:         nvidia-xconfig%{?_isa} = %{version}
%endif

Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}

Obsoletes:       %{_nvidia_serie}-kmod < %{?epoch}:%{version}
Provides:        %{_nvidia_serie}-kmod-common = %{?epoch}:%{version}
Conflicts:       xorg-x11-drv-nvidia-304xx
Conflicts:       xorg-x11-drv-nvidia-340xx
Conflicts:       xorg-x11-drv-fglrx
Conflicts:       xorg-x11-drv-catalyst

%if 0%{?fedora} || 0%{?rhel} >= 7
%global         __provides_exclude ^(lib.*GL.*\\.so.*)$
%global         __requires_exclude ^(lib.*GL.*\\.so.*)$
%else

%{?filter_setup:
%filter_from_provides /^lib.*GL.*\.so/d;
%filter_from_requires /^lib.*GL.*\.so/d;
%filter_setup
}
%endif

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with current NVIDIA chipsets series.
GF8x, GF9x, and GT2xx GPUs NOT supported by this release.

For the full product support list, please consult the release notes
http://download.nvidia.com/XFree86/Linux-x86/%{version}/README/index.html

Please use the following documentation:
http://rpmfusion.org/Howto/nVidia


%package devel
Summary:         Development files for %{name}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}

#Don't put an epoch here
Provides:        cuda-drivers-devel = %{version}-100
Provides:        cuda-drivers-devel%{?_isa} = %{version}-100

%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.

%package cuda
Summary:         CUDA driver for %{name}
Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:        nvidia-persistenced%{?_isa} = %{version}
%if 0%{?fedora}
Suggests:        nvidia-modprobe%{?_isa} = %{version}
# Boolean dependencies are only fedora
%ifarch x86_64
Requires:        (%{name}-cuda-libs(x86-32) = %{?epoch}:%{version}-%{release} if libGL(x86-32))
%endif
%else
Requires:        nvidia-modprobe%{?_isa} = %{version}
%endif
Requires:        ocl-icd%{?_isa}
Requires:        opencl-filesystem

Conflicts:       xorg-x11-drv-nvidia-340xx-cuda

#Don't put an epoch here
Provides:        cuda-drivers = %{version}-100
Provides:        cuda-drivers%{?_isa} = %{version}-100
Provides:        nvidia-driver = %{version}-100
Provides:        nvidia-driver%{?_isa} = %{version}-100

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
%if 0%{?fedora} >= 25
Requires:        libglvnd-egl%{?_isa} >= 0.2
Requires:        libglvnd-gles%{?_isa} >= 0.2
Requires:        libglvnd-glx%{?_isa} >= 0.2
Requires:        libglvnd-opengl%{?_isa} >= 0.2
Requires:        egl-wayland%{?_isa} >= 1.0.0
Requires:        mesa-libEGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGLES%{?_isa} >= 13.0.3-3
# Boolean dependencies are only fedora
%ifarch x86_64
Requires:        (%{name}-libs(x86-32) = %{?epoch}:%{version}-%{release} if libGL(x86-32))
%endif
%endif
%ifarch x86_64 i686
Requires:        vulkan-filesystem
%endif

%description libs
This package provides the shared libraries for %{name}.


%prep
%setup -q -c -T
#Only extract the needed arch
%ifarch %{ix86}
sh %{SOURCE0} \
%endif
%ifarch x86_64
sh %{SOURCE1} \
%endif
%ifarch armv7hl
sh %{SOURCE2} \
%endif
  --extract-only --target nvidiapkg-%{_target_cpu}
ln -s nvidiapkg-%{_target_cpu} nvidiapkg


%build
# Nothing to build
echo "Nothing to build"


%install
cd nvidiapkg

# Install only required libraries
mkdir -p %{buildroot}%{_libdir}
cp -a \
    libcuda.so.%{version} \
    libEGL_nvidia.so.%{version} \
    libGLESv1_CM_nvidia.so.%{version} \
    libGLESv2_nvidia.so.%{version} \
    libGLX_nvidia.so.%{version} \
    libnvcuvid.so.%{version} \
    libnvidia-cfg.so.%{version} \
    libnvidia-eglcore.so.%{version} \
    libnvidia-encode.so.%{version} \
    libnvidia-fatbinaryloader.so.%{version} \
    libnvidia-fbc.so.%{version} \
    libnvidia-glcore.so.%{version} \
    libnvidia-glsi.so.%{version} \
    libnvidia-ifr.so.%{version} \
    libnvidia-ml.so.%{version} \
    libnvidia-ptxjitcompiler.so.%{version} \
    %{buildroot}%{_libdir}/

%if 0%{?rhel} && 0%{?rhel} < 8
mkdir -p %{buildroot}%{_nvidia_libdir}
cp -a \
    libEGL.so.%{version} \
    libGL.so.%{version} \
    libGLdispatch.so.0 \
    %{buildroot}%{_nvidia_libdir}/
ldconfig -vn %{buildroot}%{_nvidia_libdir}/
%endif

# Use the correct TLS implementation for x86_64/i686, already ok on ARM
# OpenCL is only available on x86_64/i686.
%ifarch x86_64 i686
cp -af \
    tls/libnvidia-tls.so* \
    libnvidia-compiler.so.%{version} \
    libnvidia-opencl.so.%{version} \
    %{buildroot}%{_libdir}/
%else
cp -af libnvidia-tls.so* %{buildroot}%{_libdir}/
%endif

# Use ldconfig for libraries with a mismatching SONAME/filename
ldconfig -vn %{buildroot}%{_libdir}/

# Libraries you can link against
for lib in libcuda libnvcuvid libnvidia-encode; do
    ln -sf $lib.so.%{version} %{buildroot}%{_libdir}/$lib.so
done

# Vdpau driver
install -D -p -m 0755 libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
ln -sf libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.1

# GlVND
%if 0%{?rhel} && 0%{?rhel} < 8
ln -s libGLX_nvidia.so.%{version} %{buildroot}%{_libdir}/libGLX_indirect.so.0
# ld.so.conf.d file
install -m 0755 -d       %{buildroot}%{_sysconfdir}/ld.so.conf.d/
echo -e "%{_nvidia_libdir} \n" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%endif

# X DDX driver and GLX extension
install -p -D -m 0755 libglx.so.%{version} %{buildroot}%{_nvidia_xorgdir}/libglx.so.%{version}
ln -sf libglx.so.%{version} %{buildroot}%{_nvidia_xorgdir}/libglx.so
install -D -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so

%ifarch x86_64 i686
# OpenCL config
install    -m 0755         -d %{buildroot}%{_sysconfdir}/OpenCL/vendors/
install -p -m 0644 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/
# Vulkan config
sed -i -e 's|__NV_VK_ICD__|libGLX_nvidia.so.0|' nvidia_icd.json.template
install    -m 0755         -d %{buildroot}%{_datadir}/vulkan/icd.d/
install -p -m 0644 nvidia_icd.json.template %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
%if 0%{?rhel}
# back to non-glvnd version for vulkan
sed -i -e 's|libGLX_nvidia.so.0|libGL.so.1|' %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
touch -r nvidia_icd.json.template %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
%endif
%endif

# EGL config for libglvnd
install    -m 0755         -d %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
install -p -m 0644 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# Blacklist nouveau, autoload nvidia-uvm module after nvidia module
mkdir -p %{buildroot}%{_modprobe_d}
install -p -m 0644 %{SOURCE15} %{buildroot}%{_modprobe_d}
%if 0%{?rhel} && 0%{?rhel} < 8
install -p -m 0644 %{SOURCE6} %{buildroot}%{_modprobe_d}
%endif

# UDev rules for nvidia
install    -m 0755 -d          %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE11} %{buildroot}%{_udevrulesdir}

# UDev rules for nvidia-uvm
install -p -m 0644 %{SOURCE14} %{buildroot}%{_udevrulesdir}

# dracut.conf.d file, nvidia modules must never be in the initrd
install -p -m 0755 -d          %{buildroot}%{_dracut_conf_d}/
install -p -m 0644 %{SOURCE16} %{buildroot}%{_dracut_conf_d}/

# Install binaries
install -m 0755 -d %{buildroot}%{_bindir}
install -p -m 0755 nvidia-{bug-report.sh,debugdump,smi,cuda-mps-control,cuda-mps-server} \
  %{buildroot}%{_bindir}

# Install headers
install -m 0755 -d %{buildroot}%{_includedir}/nvidia/GL/
install -p -m 0644 {gl.h,glext.h,glx.h,glxext.h} %{buildroot}%{_includedir}/nvidia/GL/

# Install man pages
install    -m 0755 -d   %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{cuda-mps-control,smi}.1.gz \
  %{buildroot}%{_mandir}/man1/

#Alternate-install-present is checked by the nvidia .run
mkdir -p %{buildroot}%{_alternate_dir}
install -p -m 0644 %{SOURCE7} %{buildroot}%{_alternate_dir}

#install the NVIDIA supplied application profiles
mkdir -p %{buildroot}%{_datadir}/nvidia
install -p -m 0644 nvidia-application-profiles-%{version}-{rc,key-documentation} %{buildroot}%{_datadir}/nvidia

#Install the Xorg configuration files
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d
%if 0%{?fedora} >= 25 || 0%{?rhel} >= 7
install -pm 0644 %{SOURCE10} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
touch -r %{SOURCE10} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
%else
install -pm 0644 nvidia-drm-outputclass.conf %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
install -pm 0644 %{SOURCE4} %{buildroot}%{_datadir}/X11/xorg.conf.d
install -pm 0644 %{SOURCE5} %{buildroot}%{_datadir}/X11/xorg.conf.d
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_datadir}/X11/xorg.conf.d/99-nvidia.conf
touch -r %{SOURCE4} %{buildroot}%{_datadir}/X11/xorg.conf.d/99-nvidia.conf
%endif
#Ghost Xorg nvidia.conf files
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/nvidia.conf

#Create the default nvidia config directory
mkdir -p %{buildroot}%{_sysconfdir}/nvidia

#Install the nvidia kernel modules sources archive
mkdir -p %{buildroot}%{_datadir}/nvidia-kmod-%{version}
tar Jcf %{buildroot}%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz kernel

%if 0%{?fedora} >= 25
# install AppData and add modalias provides
mkdir -p %{buildroot}%{_datadir}/appdata/
install -pm 0644 %{SOURCE12} %{buildroot}%{_datadir}/appdata/
fn=%{buildroot}%{_datadir}/appdata/xorg-x11-drv-nvidia.metainfo.xml
%{SOURCE13} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -pm 0644 nvidia-settings.png %{buildroot}%{_datadir}/pixmaps/%{name}.png
%endif

# Install nvidia-fallback
%if 0%{?rhel} > 6 || 0%{?fedora}
mkdir -p %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE20} %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE21} %{buildroot}%{_unitdir}
%endif


%pre
if [ "$1" -eq "1" ]; then
  if [ -x %{_bindir}/nvidia-uninstall ]; then
    %{_bindir}/nvidia-uninstall -s && rm -f %{_bindir}/nvidia-uninstall &>/dev/null || :
  fi
fi

%post
if [ "$1" -eq "1" ]; then
  %{_grubby} --remove-args='nomodeset' --args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
%endif
# Until mutter enable egl stream support, we need to disable gdm wayland
# https://bugzilla.redhat.com/1462052
%if 0%{?fedora}
  if [ -f %{_sysconfdir}/gdm/custom.conf ] ; then
    sed -i -e 's/#WaylandEnable=.*/WaylandEnable=false/' %{_sysconfdir}/gdm/custom.conf
  fi
%endif
fi || :

%if 0%{?fedora} || 0%{?rhel} >= 7
%triggerun -- xorg-x11-drv-nvidia < 3:384.59-5
if [ -f %{_sysconfdir}/default/grub ] ; then
  sed -i -e '/GRUB_GFXPAYLOAD_LINUX=text/d' %{_sysconfdir}/default/grub
  . %{_sysconfdir}/default/grub
  if [ -z "${GRUB_CMDLINE_LINUX+x}" ]; then
    echo -e GRUB_CMDLINE_LINUX=\"%{_dracutopts}\" >> %{_sysconfdir}/default/grub
  else
    for i in %{_dracutopts} ; do
      _has_string=$(echo ${GRUB_CMDLINE_LINUX} | fgrep -c $i)
      if [ x"$_has_string" = x0 ] ; then
        GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} ${i}"
      fi
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
fi
%{_grubby} --args='%{_dracutopts}' &>/dev/null || :
%endif

%ldconfig_scriptlets libs
%ldconfig_scriptlets cuda-libs

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
%endif
  # Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && mv %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.nvidia_uninstalled &>/dev/null
fi ||:


%files
%license nvidiapkg/LICENSE
%doc nvidiapkg/NVIDIA_Changelog
%doc nvidiapkg/README.txt
%doc nvidiapkg/nvidia-application-profiles-%{version}-rc
%doc nvidiapkg/html
%dir %{_alternate_dir}
%{_alternate_dir}/alternate-install-present
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%dir %{_sysconfdir}/nvidia
%ghost %{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/nvidia.conf
%{_datadir}/X11/xorg.conf.d/nvidia.conf
%if 0%{?rhel} > 6 || 0%{?fedora}
%{_udevrulesdir}/10-nvidia.rules
%{_udevrulesdir}/60-nvidia.rules
%{_unitdir}/nvidia-fallback.service
%endif
%if 0%{?fedora} >= 25
%{_datadir}/appdata/%{name}.metainfo.xml
%{_datadir}/pixmaps/%{name}.png
%{_dracut_conf_d}/99-nvidia-dracut.conf
%else
# Owns the directory since libglvnd is optional here
%dir %{_datadir}/glvnd
%dir %{_datadir}/glvnd/egl_vendor.d
# RHEL6 uses /etc
%if 0%{?rhel} == 6
%config(noreplace) %{_modprobe_d}/blacklist-nouveau.conf
%config(noreplace) %{_dracut_conf_d}/99-nvidia-dracut.conf
%{_datadir}/X11/xorg.conf.d/00-avoid-glamor.conf
%{_datadir}/X11/xorg.conf.d/99-nvidia.conf
%else
%{_modprobe_d}/blacklist-nouveau.conf
%{_dracut_conf_d}/99-nvidia-dracut.conf
%endif
%endif
%{_bindir}/nvidia-bug-report.sh
# Xorg libs that do not need to be multilib
%dir %{_nvidia_xorgdir}
%{_nvidia_xorgdir}/libglx.so
%{_nvidia_xorgdir}/libglx.so.%{version}
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
#/no_multilib
%dir %{_datadir}/nvidia
%{_datadir}/nvidia/nvidia-application-profiles-%{version}-*

%files kmodsrc
%dir %{_datadir}/nvidia-kmod-%{version}
%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz

%files libs
%if 0%{?rhel} && 0%{?rhel} < 8
%config %{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%{_nvidia_libdir}/libEGL.so.1
%{_nvidia_libdir}/libEGL.so.%{version}
%{_nvidia_libdir}/libGL.so.1
%{_nvidia_libdir}/libGL.so.%{version}
%{_nvidia_libdir}/libGLdispatch.so.0
%endif
%ifarch x86_64 i686
%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
%endif
%dir %{_nvidia_libdir}
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%if 0%{?rhel}
%{_libdir}/libGLX_indirect.so.0
%endif
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-ifr.so.1
%{_libdir}/libnvidia-ifr.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}

%files cuda
%license nvidiapkg/LICENSE
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%ifarch x86_64 i686
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%endif
%{_mandir}/man1/nvidia-smi.*
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_modprobe_d}/nvidia-uvm.conf
%{_udevrulesdir}/60-nvidia-uvm.rules

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-fatbinaryloader.so.%{version}
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.1
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%ifarch x86_64 i686
%{_libdir}/libnvidia-compiler.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%endif

%files devel
%{_includedir}/nvidia/
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvidia-encode.so

%changelog
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

