%global        _nvidia_serie        nvidia
%if 0%{?fedora} >= 25
%global        _nvidia_libdir       %{_libdir}
%global        _nvidia_serie_libdir %{_libdir}/%{_nvidia_serie}
%global        _nvidia_xorgdir      %{_libdir}/%{_nvidia_serie}/xorg
%else
%global        _nvidia_libdir       %{_libdir}/%{_nvidia_serie}
%global        _nvidia_xorgdir      %{_nvidia_libdir}/xorg
%global        _glvnd_libdir        %{_libdir}/libglvnd
%endif

%if 0%{?rhel} == 6
%global        _modprobe_d          %{_sysconfdir}/modprobe.d/
# RHEL 6 does not have _udevrulesdir defined
%global        _udevrulesdir        %{_prefix}/lib/udev/rules.d/
%else
%global        _modprobe_d          %{_prefix}/lib/modprobe.d/
%endif

%global	       debug_package %{nil}
%global	       __strip /bin/true

Name:            xorg-x11-drv-nvidia
Epoch:           1
Version:         375.39
Release:         6%{?dist}
Summary:         NVIDIA's proprietary display driver for NVIDIA graphic cards

License:         Redistributable, no modification permitted
URL:             http://www.nvidia.com/
Source0:         ftp://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}.run
Source1:         ftp://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source4:         ftp://download.nvidia.com/XFree86/Linux-32bit-ARM/%{version}/NVIDIA-Linux-armv7l-gnueabihf-%{version}.run
Source2:         99-nvidia.conf
Source3:         nvidia-xorg.conf
Source5:         00-avoid-glamor.conf
Source6:         blacklist-nouveau.conf
Source7:         alternate-install-present
Source8:         nvidia-old.conf
Source9:         nvidia-settings.desktop
Source10:        nvidia.conf
Source11:        00-ignoreabi.conf
Source12:        xorg-x11-drv-nvidia.metainfo.xml
Source13:        parse-readme.py
Source14:        60-nvidia-uvm.rules
Source15:        nvidia-uvm.conf

ExclusiveArch: i686 x86_64 armv7hl

BuildRequires:    desktop-file-utils
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
%endif

Requires(post):   ldconfig
Requires(postun): ldconfig
Requires(post):   grubby
Requires:         which

Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
%if 0%{?fedora} >= 25
# filesystem is needed as we don't own %%{_libdir}
Requires:        filesystem
Requires:        xorg-x11-server-Xorg%{?_isa} >= 1.19.0-3
%endif

Obsoletes:       %{_nvidia_serie}-kmod < %{?epoch}:%{version}
Provides:        %{_nvidia_serie}-kmod-common = %{?epoch}:%{version}
Conflicts:       xorg-x11-drv-nvidia-beta
Conflicts:       xorg-x11-drv-nvidia-legacy
Conflicts:       xorg-x11-drv-nvidia-71xx
Conflicts:       xorg-x11-drv-nvidia-96xx
Conflicts:       xorg-x11-drv-nvidia-173xx
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
Requires:        %{name}-cuda = %{?epoch}:%{version}-%{release}
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
Provides:        nvidia-persistenced = %{version}-%{release}
Requires:        ocl-icd%{?_isa}
Requires:        opencl-filesystem

Conflicts:       xorg-x11-drv-nvidia-340xx-cuda

#Don't put an epoch here
Provides:        cuda-drivers = %{version}-100
Provides:        cuda-drivers%{?_isa} = %{version}-100

%description cuda
This package provides the CUDA driver.

%package cuda-libs
Summary:         CUDA libraries for %{name}
Requires:        %{name}-cuda = %{?epoch}:%{version}-%{release}

%description cuda-libs
This package provides the CUDA driver libraries.

%package kmodsrc
Summary:         %{name} kernel module source code

%description kmodsrc
Source tree used for building kernel module packages (%{name}-kmod)
which is generated during the build of main package.

%package libs
Summary:         Libraries for %{name}
Requires:        %{name} = %{?epoch}:%{version}-%{release}
Requires:        libvdpau%{?_isa} >= 0.5
Requires:        libglvnd%{?_isa} >= 0.2
%if 0%{?fedora} >= 25
Requires:        egl-wayland%{?_isa} >= 1.0.0
Requires:        libglvnd-egl%{?_isa} >= 0.2
Requires:        libglvnd-gles%{?_isa} >= 0.2
Requires:        libglvnd-glx%{?_isa} >= 0.2
Requires:        libglvnd-opengl%{?_isa} >= 0.2
Requires:        mesa-libEGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGLES%{?_isa} >= 13.0.3-3
# Boolean dependencies are not yet allowed in fedora, only for testing
%if 0%{?fedora} >= 26
%ifarch x86_64
Requires:        (%{name}-libs(x86-32) = %{?epoch}:%{version}-%{release} if libGL(x86-32))
%endif
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
sh %{SOURCE4} \
%endif
  --extract-only --target nvidiapkg-%{_target_cpu}
ln -s nvidiapkg-%{_target_cpu} nvidiapkg


%build
# Nothing to build
echo "Nothing to build"


%install
rm -rf $RPM_BUILD_ROOT

cd nvidiapkg

# The new 256.x version supplies all the files in a relatively flat structure
# .. so explicitly deal out the files to the correct places
# .. nvidia-installer looks too closely at the current machine, so it's hard
# .. to generate rpm's unless a NVIDIA card is in the machine.

rm -f nvidia-installer*

# GLVND
rm libGL.so*
rm libEGL.so*

# Built from source
rm -f libnvidia-egl-wayland.so*

# Simple wildcard install of libs
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_libdir}
install -p -m 0755 lib*.so.%{version}          $RPM_BUILD_ROOT%{_nvidia_libdir}/
%ifarch x86_64 i686
# Use only newer ELF TLS implementation
install -p -m 0755 tls/lib*.so.%{version}      $RPM_BUILD_ROOT%{_nvidia_libdir}/
%endif

# GlVND
ln -s libGLX_nvidia.so.%{version} $RPM_BUILD_ROOT%{_nvidia_libdir}/libGLX_indirect.so.0

# Fix unowned lib links
ln -s libEGL_nvidia.so.%{version} $RPM_BUILD_ROOT%{_nvidia_libdir}/libEGL_nvidia.so.0
ln -s libGLESv2_nvidia.so.%{version} $RPM_BUILD_ROOT%{_nvidia_libdir}/libGLESv2_nvidia.so.2
ln -s libGLX_nvidia.so.%{version} $RPM_BUILD_ROOT%{_nvidia_libdir}/libGLX_nvidia.so.0

%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
#Workaround for cuda availability - rfbz#2916
ln -fs %{_nvidia_libdir}/libcuda.so.1 $RPM_BUILD_ROOT%{_libdir}/libcuda.so.1
ln -fs %{_nvidia_libdir}/libcuda.so $RPM_BUILD_ROOT%{_libdir}/libcuda.so
%endif

%ifarch x86_64 i686
# OpenCL config
install    -m 0755         -d $RPM_BUILD_ROOT%{_sysconfdir}/OpenCL/vendors/
install -p -m 0644 nvidia.icd $RPM_BUILD_ROOT%{_sysconfdir}/OpenCL/vendors/
# Vulkan config
install    -m 0755         -d $RPM_BUILD_ROOT%{_sysconfdir}/vulkan/icd.d/
install -p -m 0644 nvidia_icd.json $RPM_BUILD_ROOT%{_sysconfdir}/vulkan/icd.d/
%endif
# EGL config
install    -m 0755         -d $RPM_BUILD_ROOT%{_sysconfdir}/glvnd/egl_vendor.d/
install -p -m 0644 10_nvidia.json $RPM_BUILD_ROOT%{_sysconfdir}/glvnd/egl_vendor.d/

#Vdpau
install -m 0755 -d $RPM_BUILD_ROOT%{_libdir}/vdpau/
install -p -m 0755 libvdpau*.so.%{version}     $RPM_BUILD_ROOT%{_libdir}/vdpau

#
mkdir -p $RPM_BUILD_ROOT%{_libdir}/xorg/modules/drivers/
mkdir -p $RPM_BUILD_ROOT%{_nvidia_xorgdir}

# .. but some in a different place
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_xorgdir}
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_xorgdir}
rm -f $RPM_BUILD_ROOT%{_nvidia_libdir}/lib{nvidia-wfb,glx,vdpau*}.so.%{version}

# Finish up the special case libs
install -p -m 0755 libglx.so.%{version}        $RPM_BUILD_ROOT%{_nvidia_xorgdir}
install -p -m 0755 nvidia_drv.so               $RPM_BUILD_ROOT%{_libdir}/xorg/modules/drivers/

# ld.so.conf.d file
%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
install -m 0755 -d       $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
echo -e "%{_nvidia_libdir} \n%{_glvnd_libdir} \n" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%endif

# Blacklist nouveau, autoload nvidia-uvm module after nvidia module
install    -m 0755 -d                     $RPM_BUILD_ROOT%{_modprobe_d}/
install -p -m 0644 %{SOURCE6} %{SOURCE15} $RPM_BUILD_ROOT%{_modprobe_d}/

# UDev rules for nvidia-uvm
install    -m 0755 -d          $RPM_BUILD_ROOT%{_udevrulesdir}
install -p -m 0644 %{SOURCE14} $RPM_BUILD_ROOT%{_udevrulesdir}

# Install binaries
install -m 0755 -d $RPM_BUILD_ROOT%{_bindir}
install -p -m 0755 nvidia-{bug-report.sh,debugdump,smi,cuda-mps-control,cuda-mps-server,xconfig,settings,persistenced} \
  $RPM_BUILD_ROOT%{_bindir}

# Install headers
install -m 0755 -d $RPM_BUILD_ROOT%{_includedir}/nvidia/GL/
install -p -m 0644 {gl.h,glext.h,glx.h,glxext.h} $RPM_BUILD_ROOT%{_includedir}/nvidia/GL/

# Install man pages
install    -m 0755 -d   $RPM_BUILD_ROOT%{_mandir}/man1/
install -p -m 0644 nvidia-{cuda-mps-control,persistenced,settings,smi,xconfig}.1.gz \
  $RPM_BUILD_ROOT%{_mandir}/man1/

# Make unversioned links to dynamic libs
for lib in $( find $RPM_BUILD_ROOT%{_libdir} -name lib\*.%{version} ) ; do
  ln -s ${lib##*/} ${lib%.%{version}}
  ln -s ${lib##*/} ${lib%.%{version}}.1
done


# Install nvidia icon
mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -pm 0644 nvidia-settings.png $RPM_BUILD_ROOT%{_datadir}/pixmaps

# Remove duplicate install
rm $RPM_BUILD_ROOT%{_nvidia_libdir}/libnvidia-{cfg,tls}.so

#Install static driver dependant configuration files
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
install -pm 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
%endif
install -pm 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/X11/
%if 0%{?fedora} <= 24
install -pm 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
sed -i -e 's|@LIBDIR@|%{_libdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch -r %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%endif
# Comment Xorg abi override
#install -pm 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d

# Fix desktop file and validate
sed -i -e 's|__UTILS_PATH__/||g' -e 's|__PIXMAP_PATH__/||g' nvidia-settings.desktop
sed -i -e 's|nvidia-settings.png|nvidia-settings|g' nvidia-settings.desktop
desktop-file-install --vendor "" \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications/ \
    nvidia-settings.desktop

%if 0%{?rhel} < 8 || 0%{?fedora} <= 24
#Workaround for self made xorg.conf using a Files section.
ln -fs ../../%{_nvidia_serie}/xorg $RPM_BUILD_ROOT%{_libdir}/xorg/modules/%{_nvidia_serie}-%{version}
%endif

#Alternate-install-present is checked by the nvidia .run
install -p -m 0644 %{SOURCE7}            $RPM_BUILD_ROOT%{_nvidia_libdir}

#install the NVIDIA supplied application profiles
mkdir -p $RPM_BUILD_ROOT%{_datadir}/nvidia
install -p -m 0644 nvidia-application-profiles-%{version}-{rc,key-documentation} $RPM_BUILD_ROOT%{_datadir}/nvidia

#Install the output class configuration file - xorg-server >= 1.16
%if 0%{?fedora} >= 25
mkdir -p $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d
install -pm 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d/nvidia.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d/nvidia.conf
touch -r %{SOURCE10} $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d/nvidia.conf
%endif
%if 0%{?rhel} == 7 || 0%{?fedora} == 24
mkdir -p $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d
install -pm 0644 %{SOURCE8} $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d/nvidia.conf
%endif

#Install the initscript
tar jxf nvidia-persistenced-init.tar.bz2
%if 0%{?rhel} > 6 || 0%{?fedora}
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -pm 0644 nvidia-persistenced-init/systemd/nvidia-persistenced.service.template \
  $RPM_BUILD_ROOT%{_unitdir}/nvidia-persistenced.service
#Change the daemon running owner
sed -i -e "s/__USER__/root/" $RPM_BUILD_ROOT%{_unitdir}/nvidia-persistenced.service
%endif

#Create the default nvidia config directory
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/nvidia

#Ghost Xorg nvidia.conf file
touch $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/nvidia.conf

#Install the nvidia kernel modules sources archive
mkdir -p $RPM_BUILD_ROOT%{_datadir}/nvidia-kmod-%{version}
tar Jcf $RPM_BUILD_ROOT%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz kernel

#Add autostart file for nvidia-settings to load user config
install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/nvidia-settings.desktop

%if 0%{?fedora} >= 25
# install AppData and add modalias provides
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata/
install -pm 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_datadir}/appdata/
fn=$RPM_BUILD_ROOT%{_datadir}/appdata/xorg-x11-drv-nvidia.metainfo.xml
%{SOURCE13} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
%endif


%pre
if [ "$1" -eq "1" ]; then
  if [ -x %{_bindir}/nvidia-uninstall ]; then
    %{_bindir}/nvidia-uninstall -s && rm -f %{_bindir}/nvidia-uninstall &>/dev/null || :
  fi
fi

%post
/sbin/ldconfig
if [ "$1" -eq "1" ]; then
  ISGRUB1=""
  if [[ -f /boot/grub/grub.conf && ! -f /boot/grub2/grub.cfg ]] ; then
      ISGRUB1="--grub"
      GFXPAYLOAD="vga=normal"
  else
      #echo "GRUB_GFXPAYLOAD_LINUX=text" >> %{_sysconfdir}/default/grub
      if [ -f /boot/grub2/grub.cfg ]; then
        /sbin/grub2-mkconfig -o /boot/grub2/grub.cfg
      fi
      if [ -f /boot/efi/EFI/fedora/grub.cfg ]; then
        /sbin/grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
      fi
  fi
  if [ -x /sbin/grubby ] ; then
    KERNELS=`/sbin/grubby --default-kernel`
    DIST=`rpm -E %%{?dist}`
    ARCH=`uname -m`
    [ -z $KERNELS ] && KERNELS=`ls /boot/vmlinuz-*${DIST}.${ARCH}*`
    for kernel in ${KERNELS} ; do
      /sbin/grubby $ISGRUB1 \
        --update-kernel=${kernel} \
        --args="nouveau.modeset=0 rd.driver.blacklist=nouveau $GFXPAYLOAD" \
         &>/dev/null
    done
  fi
fi || :


%post libs -p /sbin/ldconfig

%post cuda
/sbin/ldconfig
%if 0%{?rhel} > 6 || 0%{?fedora}
%systemd_post nvidia-persistenced.service
%endif

%post cuda-libs -p /sbin/ldconfig


%preun
if [ "$1" -eq "0" ]; then
  ISGRUB1=""
  if [[ -f /boot/grub/grub.conf && ! -f /boot/grub2/grub.cfg ]] ; then
      ISGRUB1="--grub"
  else
    sed -i -e 's|GRUB_GFXPAYLOAD_LINUX=text||g' /etc/default/grub
      if [ -f /boot/grub2/grub.cfg ]; then
        /sbin/grub2-mkconfig -o /boot/grub2/grub.cfg
      fi
      if [ -f /boot/efi/EFI/fedora/grub.cfg ]; then
        /sbin/grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
      fi
  fi
  if [ -x /sbin/grubby ] ; then
    DIST=`rpm -E %%{?dist}`
    ARCH=`uname -m`
    KERNELS=`ls /boot/vmlinuz-*${DIST}.${ARCH}*`
    for kernel in ${KERNELS} ; do
      /sbin/grubby $ISGRUB1 \
        --update-kernel=${kernel} \
        --remove-args="nouveau.modeset=0 rdblacklist=nouveau \
            rd.driver.blacklist=nouveau nomodeset video=vesa:off \
            gfxpayload=vga=normal vga=normal" &>/dev/null
    done
  fi

  #Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && \
    mv  %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.%{name}_uninstalled &>/dev/null
fi ||:

%if 0%{?rhel} > 6 || 0%{?fedora}
%preun cuda
%systemd_preun nvidia-persistenced.service
%endif

%postun -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%postun cuda
/sbin/ldconfig
%if 0%{?rhel} > 6 || 0%{?fedora}
%systemd_postun_with_restart nvidia-persistenced.service
%endif

%postun cuda-libs -p /sbin/ldconfig

%files
%license nvidiapkg/LICENSE
%doc nvidiapkg/NVIDIA_Changelog
%doc nvidiapkg/README.txt
%doc nvidiapkg/nvidia-application-profiles-%{version}-rc
%doc nvidiapkg/html
%ifarch x86_64 i686
%config %{_sysconfdir}/vulkan/icd.d/nvidia_icd.json
%endif
%config %{_sysconfdir}/glvnd/egl_vendor.d/10_nvidia.json
%dir %{_sysconfdir}/nvidia
%ghost  %{_sysconfdir}/X11/xorg.conf.d/nvidia.conf
%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
%config %{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%config %{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
%endif
# Comment Xorg abi override
#%%config %%{_sysconfdir}/X11/xorg.conf.d/00-ignoreabi.conf
%config(noreplace) %{_modprobe_d}/blacklist-nouveau.conf
%config(noreplace) %{_sysconfdir}/X11/nvidia-xorg.conf
%config %{_sysconfdir}/xdg/autostart/nvidia-settings.desktop
%{_bindir}/nvidia-bug-report.sh
%{_bindir}/nvidia-settings
%{_bindir}/nvidia-xconfig
# Xorg libs that do not need to be multilib
%if 0%{?fedora} >= 25
%{_nvidia_serie_libdir}
%endif
%{_nvidia_xorgdir}
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%if 0%{?rhel} < 8 || 0%{?fedora} <= 24
%{_libdir}/xorg/modules/%{_nvidia_serie}-%{version}
%endif
# It's time that nvidia-settings used gtk3
%ifarch %{arm}
%{_nvidia_libdir}/libnvidia-gtk2.so*
%else
%exclude %{_nvidia_libdir}/libnvidia-gtk2.so*
%{_nvidia_libdir}/libnvidia-gtk3.so*
%endif
#/no_multilib
%if 0%{?rhel} > 6 || 0%{?fedora}
%{_datadir}/X11/xorg.conf.d/nvidia.conf
%endif
%if 0%{?fedora} >= 25
%{_datadir}/appdata/xorg-x11-drv-nvidia.metainfo.xml
%endif
%dir %{_datadir}/nvidia
%{_datadir}/nvidia/nvidia-application-profiles-%{version}-*
%{_datadir}/applications/*nvidia-settings.desktop
%{_datadir}/pixmaps/*.png
%{_mandir}/man1/nvidia-settings.*
%{_mandir}/man1/nvidia-xconfig.*

%files kmodsrc
%dir %{_datadir}/nvidia-kmod-%{version}
%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz

%files libs
%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
%config %{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%dir %{_nvidia_libdir}
%endif
%{_nvidia_libdir}/alternate-install-present
%{_nvidia_libdir}/*.so.*
%exclude %{_nvidia_libdir}/libcuda.so*
%exclude %{_nvidia_libdir}/libnvidia-gtk*.so*
%exclude %{_nvidia_libdir}/libnvcuvid.so*
%exclude %{_nvidia_libdir}/libnvidia-encode.so*
%exclude %{_nvidia_libdir}/libnvidia-fatbinaryloader.so*
%exclude %{_nvidia_libdir}/libnvidia-ml.so*
%exclude %{_nvidia_libdir}/libnvidia-ptxjitcompiler.so*
%ifarch x86_64 i686
%exclude %{_nvidia_libdir}/libnvidia-compiler.so*
%exclude %{_nvidia_libdir}/libnvidia-opencl.so*
%endif
%{_libdir}/vdpau/libvdpau_nvidia.so.*

%files cuda
%license nvidiapkg/LICENSE
%if 0%{?rhel} > 6 || 0%{?fedora}
%{_unitdir}/nvidia-persistenced.service
%endif
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-persistenced
%if 0%{?rhel} > 6 || 0%{?fedora} <= 24
%{_libdir}/libcuda.so*
%endif
%{_nvidia_libdir}/libnvidia-fatbinaryloader.so*
%{_nvidia_libdir}/libnvidia-ml.so*
%{_nvidia_libdir}/libnvidia-ptxjitcompiler.so*
%ifarch x86_64 i686
%{_nvidia_libdir}/libnvidia-compiler.so*
%{_nvidia_libdir}/libnvidia-opencl.so*
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%endif
%{_mandir}/man1/nvidia-smi.*
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-persistenced.1.*
%{_modprobe_d}/nvidia-uvm.conf
%{_udevrulesdir}/60-nvidia-uvm.rules

%files cuda-libs
%{_nvidia_libdir}/libcuda.so*
%{_nvidia_libdir}/libnvcuvid.so*
%{_nvidia_libdir}/libnvidia-encode.so*

%files devel
%{_includedir}/nvidia/
%{_libdir}/vdpau/libvdpau_nvidia.so
%{_nvidia_libdir}/libnvidia-ifr.so
%{_nvidia_libdir}/libEGL_nvidia.so
%{_nvidia_libdir}/libGLESv1_CM_nvidia.so
%{_nvidia_libdir}/libGLESv2_nvidia.so
%{_nvidia_libdir}/libnvidia-eglcore.so
%{_nvidia_libdir}/libnvidia-fbc.so
%{_nvidia_libdir}/libnvidia-glcore.so
%{_nvidia_libdir}/libnvidia-glsi.so
%{_nvidia_libdir}/libGLX_nvidia.so

%changelog
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

* Mon Oct 24 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:375.10-2
- Add glvnd/egl_vendor.d file
- Add requires vulkan-filesystem

* Fri Oct 21 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:375.10-1
- Update to 375.10 beta release
- Clean up more libglvnd provided libs

* Wed Oct 12 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-5
- Add libglvnd path to ld.so.conf.d conf file

* Tue Oct 11 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-4
- Switch to system libglvnd
- Fix unowned file links

* Fri Sep 30 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-3
- add xorg abi override

* Tue Sep 13 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-2
- readd libGLdispatch.so.0

* Fri Sep 09 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-1
- Update to 370.28
- Remove surplus glvnd libs (not used)
- Prepare for fedora glvnd package

* Fri Aug 19 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.23-1
- Update to 370.23 beta

* Wed Aug 10 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-3
- Revert last commit
- add ldconfig in %%post and %%postun for main package rfbz#3998

* Wed Aug 10 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-2
- Move setttings libs to libs sub-package rfbz#3998

* Sun Jul 17 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-1
- Update to 367.35

* Sat Jul 16 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.27-2
- Add vulkan icd profile

* Fri Jul 01 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.27-1
- Update to 367.27

* Wed Jun 22 2016 Nicolas Chauvet <kwizart@gmail.com> - 1:367.27-1
- Update to 367.27

* Wed Jan 27 2016 Nicolas Chauvet <kwizart@gmail.com> - 1:358.16-2
- Enforce GRUB_GFXPAYLOAD_LINUX=text even for EFI - prevent this message:
  The NVIDIA Linux graphics driver requires the use of a text-mode VGA console
  Use of other console drivers including, but not limited to, vesafb, may
  result in corruption and stability problems, and is not supported.
  To verify , check cat /proc/driver/nvidia/./warnings/fbdev

* Sat Nov 21 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:358.16-1
- Update to 358.16
- Remove posttrans for fedora < 21
- Remove ignoreabi config file as it rarely works

* Mon Aug 31 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:355.11-1
- Update to 355.11

* Fri Aug 28 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.41-1
- Update to 352.41

* Tue Jul 28 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.30-1
- Update to 352.30

* Mon Jun 15 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.21-1
- Update to 352.21

* Wed May 20 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.72-1
- Update to 343.72

* Wed Apr 08 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.59-1
- Update to 343.59

* Tue Feb 24 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.47-1
- Update to 343.47

* Sun Feb 15 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:346.35-4
- Fix build for armhfp

* Mon Jan 26 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:346.35-3
- Add cuda-driver-devel and %%{_isa} virtual provides

* Wed Jan 21 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.35-2
- clean up gtk from libs sub-package

* Fri Jan 16 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.35-1
- Update to 346.35

* Sun Jan 11 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:343.36-2
- Move libnvidia-ml back into -cuda along with nvidia-debugdump
