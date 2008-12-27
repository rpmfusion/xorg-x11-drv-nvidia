%define        nvidialibdir      %{_libdir}/nvidia

# Tweak to have debuginfo - part 1/2
%if 0%{?fedora} >= 7
%define __debug_install_post %{_builddir}/%{?buildsubdir}/find-debuginfo.sh %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

Name:            xorg-x11-drv-nvidia
Version:         180.18
Release:         1%{?dist}
Summary:         NVIDIA's proprietary display driver for NVIDIA graphic cards

Group:           User Interface/X Hardware Support
License:         Redistributable, no modification permitted
URL:             http://www.nvidia.com/
Source0:         ftp://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}-pkg0.run
Source1:         ftp://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}-pkg0.run
Source4:         nvidia-settings.desktop
Source5:         nvidia-init
Source10:        nvidia-config-display
Source11:        nvidia-README.Fedora
# So we don't pull other nvidia variants
Source91:        filter-requires.sh
%define          _use_internal_dependency_generator 0
%define          __find_requires %{SOURCE91}

BuildRoot:       %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:   i386 x86_64

Requires:        nvidia-kmod >= %{version}
Requires(post):  nvidia-kmod >= %{version}

# Needed in all nvidia or fglrx driver packages
BuildRequires:   desktop-file-utils
Requires:        which
Requires:        livna-config-display >= 0.0.21
Requires:        %{name}-libs-%{_target_cpu} = %{version}-%{release}

Requires(post):  livna-config-display
Requires(preun): livna-config-display
Requires(post):  chkconfig
Requires(post):  ldconfig
Requires(preun): chkconfig

Provides:        nvidia-kmod-common = %{version}
Conflicts:       xorg-x11-drv-nvidia-legacy
Conflicts:       xorg-x11-drv-nvidia-96xx
Conflicts:       xorg-x11-drv-nvidia-173xx
Conflicts:       xorg-x11-drv-nvidia-beta
Conflicts:       xorg-x11-drv-fglrx
Obsoletes:       nvidia-kmod < %{version}

Obsoletes:       nvidia-x11-drv < %{version}-%{release}
Provides:        nvidia-x11-drv = %{version}-%{release}

Obsoletes:       xorg-x11-drv-nvidia-newest < %{version}-100
Provides:        xorg-x11-drv-nvidia-newest = %{version}-101


%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with NVIDIA chipsets GeForce6 series and newer.
GeForce5 and below are NOT supported by this release.

For the full product support list, please consult the release notes
for driver version %{version}.


%package devel
Summary:         Development files for %{name}
Group:           Development/Libraries
Requires:        %{name}-libs = %{version}-%{release}

%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.

%package libs
Summary:         Libraries for %{name}
Group:           User Interface/X Hardware Support
Requires:        %{name} = %{version}-%{release}
Provides:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
%ifarch %{ix86}
Provides:        %{name}-libs-32bit = %{version}-%{release}
Obsoletes:       %{name}-libs-32bit <= %{version}-%{release}
Obsoletes:       nvidia-x11-drv-32bit < %{version}-%{release}
Provides:        nvidia-x11-drv-32bit = %{version}-%{release}
%endif

%description libs
This package provides the shared libraries for %{name}.


%prep
%setup -q -c -T
sh %{SOURCE0} --extract-only --target nvidiapkg-x86
sh %{SOURCE1} --extract-only --target nvidiapkg-x64
tar -cjf nvidia-kmod-data-%{version}.tar.bz2 nvidiapkg-*/LICENSE nvidiapkg-*/usr/src/

# Tweak to have debuginfo - part 2/2
%if 0%{?fedora} >= 7
cp -p %{_prefix}/lib/rpm/find-debuginfo.sh .
sed -i -e 's|strict=true|strict=false|' find-debuginfo.sh
%endif

%ifarch %{ix86}
ln -s nvidiapkg-x86 nvidiapkg
%else
ln -s nvidiapkg-x64 nvidiapkg
%endif
mv nvidiapkg/LICENSE nvidiapkg/usr/share/doc/
# More docs
cp %{SOURCE11} nvidiapkg/usr/share/doc/README.Fedora
find nvidiapkg/usr/share/doc/ -type f | xargs chmod 0644


%build
# Nothing to build
echo "Nothing to build"


%install
rm -rf $RPM_BUILD_ROOT

set +x
for file in $(cd nvidiapkg &> /dev/null; find . -type f | grep -v -e 'makeself.sh$' -e 'mkprecompiled$' -e 'tls_test$' -e 'tls_test_dso.so$' -e 'nvidia-settings.desktop$' -e '^./Makefile'  -e '^./nvidia-installer' -e '^./pkg-history.txt' -e '^./.manifest' -e '/usr/share/doc/' -e 'libGL.la$' -e 'drivers/nvidia_drv.o$' -e 'nvidia-installer.1.gz$' -e '^./usr/src/')
do
  if [[ ! "/${file##./usr/lib/}" = "/${file}" ]]
  then
    install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/%{nvidialibdir}/${file##./usr/lib/}
  elif [[ ! "/${file##./usr/X11R6/lib/modules/extensions}" = "/${file}" ]]
  then
    install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/%{_libdir}/xorg/modules/extensions/nvidia/${file##./usr/X11R6/lib/modules/extensions}
  elif [[ ! "/${file##./usr/X11R6/lib/modules}" = "/${file}" ]]
  then
    install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/%{_libdir}/xorg/modules/${file##./usr/X11R6/lib/modules}
  elif [[ ! "/${file##./usr/X11R6/lib/}" = "/${file}" ]]
  then
    install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/%{nvidialibdir}/${file##./usr/X11R6/lib/}
  elif [[ ! "/${file##./usr/include/}" = "/${file}" ]]
  then
    install -D -p -m 0644 nvidiapkg/${file} $RPM_BUILD_ROOT/%{_includedir}/nvidia/${file##./usr/include/}
  elif [[ ! "/${file##./usr/bin/}" = "/${file}" ]]
  then
    if [[ ! "/${file##./usr/bin/nvidia-xconfig}" = "/${file}" ]]
    then
      install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/usr/sbin/${file##./usr/bin/}
    elif [[ ! "/${file##./usr/bin/nvidia-bug-report.sh}" = "/${file}" ]]
    then
      install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/usr/bin/${file##./usr/bin/}
    else
      install -D -p -m 0755 nvidiapkg/${file} $RPM_BUILD_ROOT/${file}
    fi
  elif [[ ! "/${file##./usr/share/man/}" = "/${file}" ]]
  then
    install -D -p -m 0644 nvidiapkg/${file} $RPM_BUILD_ROOT/%{_mandir}/${file##./usr/share/man/}
    gunzip $RPM_BUILD_ROOT/%{_mandir}/${file##./usr/share/man/}
  elif [[ ! "/${file##./usr/share/pixmaps/}" = "/${file}" ]]
  then
    install -D -p -m 0644 nvidiapkg/${file} $RPM_BUILD_ROOT/%{_datadir}/pixmaps/${file##./usr/share/pixmaps/}
  else
    echo ${file} found -- don\'t know how to handle
    exit 1
  fi
done
set -x

# Move the libnvidia-wfb.so lib to the Nvidia xorg extension directory.
mv $RPM_BUILD_ROOT%{_libdir}/xorg/modules/libnvidia-wfb.so.%{version} $RPM_BUILD_ROOT%{_libdir}/xorg/modules/extensions/nvidia/libnvidia-wfb.so.%{version}

# Fixme: should we do this directly in above for-loop? Yes, we should! No, please don't!
ln -s libGLcore.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libGLcore.so
ln -s libGLcore.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libGLcore.so.1
ln -s libGL.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libGL.so
ln -s libGL.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libGL.so.1
ln -s libnvidia-tls.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libnvidia-tls.so.1
ln -s libnvidia-tls.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/tls/libnvidia-tls.so.1
ln -s libnvidia-cfg.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libnvidia-cfg.so.1
ln -s libXvMCNVIDIA.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libXvMCNVIDIA.so
ln -s libXvMCNVIDIA.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libXvMCNVIDIA_dynamic.so.1
ln -s libglx.so.%{version} $RPM_BUILD_ROOT%{_libdir}/xorg/modules/extensions/nvidia/libglx.so


# This is 97xx specific. libnvidia-wfb.so is a replacement of libwfb.so
# It is used by card > NV30 but required by G80 and newer.
%if 0%{?fedora} >= 9
rm -rf $RPM_BUILD_ROOT%{_libdir}/xorg/modules/extensions/nvidia/libnvidia-wfb.so.%{version}
%else
ln -s libnvidia-wfb.so.%{version} $RPM_BUILD_ROOT%{_libdir}/xorg/modules/extensions/nvidia/libnvidia-wfb.so.1
ln -s libnvidia-wfb.so.%{version} $RPM_BUILD_ROOT%{_libdir}/xorg/modules/extensions/nvidia/libwfb.so
%endif

# This is 169.04 adds - cuda libs and headers
ln -s libcuda.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libcuda.so.1
ln -s libcuda.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libcuda.so

# This is 180.xx adds - vdpau libs and headers
ln -s libvdpau_nvidia.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libvdpau_nvidia.so
ln -s libvdpau.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libvdpau.so.1
ln -s libvdpau.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libvdpau.so
ln -s libvdpau_trace.so.%{version} $RPM_BUILD_ROOT%{nvidialibdir}/libvdpau_trace.so

# X configuration script
install -D -p -m 0755 %{SOURCE10} $RPM_BUILD_ROOT%{_sbindir}/nvidia-config-display

# Desktop entry for nvidia-settings
desktop-file-install --vendor livna \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications/ \
    %{SOURCE4}

# Install initscript
install -D -p -m 0755 %{SOURCE5} $RPM_BUILD_ROOT%{_initrddir}/nvidia

# ld.so.conf.d file
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
echo "%{nvidialibdir}" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

# Change perms on static libs. Can't fathom how to do it nicely above.
find $RPM_BUILD_ROOT/%{nvidialibdir} -type f -name "*.a" -exec chmod 0644 '{}' \;



%clean
rm -rf $RPM_BUILD_ROOT


%post
# Removes old legacy layout, fixed SELinux copy errors
if [ ! $(ls /etc/udev/devices/nvidia* 2>/dev/null | wc -l) -eq 0 ];then rm -f /etc/udev/devices/nvidia*;fi ||:
if [ "$1" -eq "1" ]; then
  # Enable nvidia driver when installing
  %{_sbindir}/nvidia-config-display enable &>/dev/null ||:
  # Add init script and start it
  /sbin/chkconfig --add nvidia ||:
  /etc/init.d/nvidia start &>/dev/null ||:
fi

%post libs -p /sbin/ldconfig

%preun
if [ "$1" -eq "0" ]; then
    # Disable driver on final removal
    test -f %{_sbindir}/nvidia-config-display && %{_sbindir}/nvidia-config-display disable &>/dev/null ||:
    %{_initrddir}/nvidia stop &> /dev/null ||:
    /sbin/chkconfig --del nvidia ||:
fi ||:

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc nvidiapkg/usr/share/doc/*
%{_initrddir}/nvidia
%{_bindir}/*
%{_sbindir}/*
# Xorg libs that do not need to be multilib
%dir %{_libdir}/xorg/modules/extensions/nvidia
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_libdir}/xorg/modules/extensions/nvidia/*.so*
#/no_multilib
%{_datadir}/applications/*nvidia-settings.desktop
%{_datadir}/pixmaps/*.png
%{_mandir}/man[1-9]/nvidia*.*

%files libs
%defattr(-,root,root,-)
%dir %{nvidialibdir}
%dir %{nvidialibdir}/tls
%config %{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%{nvidialibdir}/*.so.*
%{nvidialibdir}/libGLcore.so
%{nvidialibdir}/libvdpau_nvidia.so
%{nvidialibdir}/libvdpau_trace.so
%{nvidialibdir}/tls/*.so.*

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/nvidia
%dir %{_includedir}/nvidia/GL
%dir %{_includedir}/nvidia/cuda
%dir %{_includedir}/nvidia/vdpau
%{_includedir}/nvidia/GL/*.h
%{_includedir}/nvidia/cuda/*.h
%{_includedir}/nvidia/vdpau/*.h
%exclude %{nvidialibdir}/libXvMCNVIDIA.a
%{nvidialibdir}/libcuda.so
%{nvidialibdir}/libGL.so
%{nvidialibdir}/libvdpau.so
%{nvidialibdir}/libXvMCNVIDIA.so


%changelog
* Sat Dec 28 2008 kwizart < kwizart at gmail.com > - 180.18-1
- Update to 180.18 (beta)

* Wed Dec 17 2008 kwizart < kwizart at gmail.com > - 180.16-1
- Update to 180.16 (beta)
- Exclude libXvMCNVIDIA.a
- More accurate -devel subpackage.

* Tue Dec 2 2008 Stewart Adam <s.adam at diffingo.com> - 177.82-2
- Fix upgrade path for nvidia-newest (bz#191)

* Thu Nov 13 2008 kwizart < kwizart at gmail.com > - 177.82-1
- Update to 177.82

* Wed Nov 12 2008 kwizart < kwizart at gmail.com > - 177.80-6
- Obsoletes/Provides xorg-x11-drv-nvidia-newest
- Cleaning
- Improve description

* Tue Nov 4 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-5
- Fix upgrade path for FreshRPMs users

* Mon Oct 27 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-4
- Revert the libs dep change

* Sat Oct 25 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-3
- Remove the libs subpackage's dependency on main package
- Update dependency on livna-config-display

* Sat Oct 18 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-2
- Change dependency of main package to libs subpackage in devel subpackage to
  fix multiarch repo push

* Mon Oct 13 2008 kwizart < kwizart at gmail.com > - 177.80-1
- Update to 177.80
- Move symlinks in -devel
- Fix description

* Sun Oct 05 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 177.78-2
- rebuild for rpm fusion

* Wed Oct 1 2008 Stewart Adam < s.adam at diffingo.com > - 177.78-1
- Update to 177.78 (beta)

* Mon Sep 15 2008 Stewart Adam < s.adam at diffingo.com > - 177.70-1
- Update to 177.70 (beta)

* Thu Jul 31 2008 kwizart < kwizart at gmail.com > - 173.14.12-1
- Update to 173.14.12

* Tue Jun 17 2008 kwizart < kwizart at gmail.com > - 173.14.09-1
- Update to 173.14.09

* Wed May 28 2008 Stewart Adam <s.adam at diffingo.com> - 173.14.05-2
- Only modify modprobe.conf if it exists

* Wed May 28 2008 kwizart < kwizart at gmail.com > - 173.14.05-1
- Update to 173.14.05

* Wed May 14 2008 kwizart < kwizart at gmail.com > - 173.08-2
- Fix libwfb replacement - Not needed on Fedora >= 9

* Thu Apr 10 2008 kwizart < kwizart at gmail.com > - 173.08-1
- Update to 173.08 (beta) - Fedora 9 experimental support
  See: http://www.nvnews.net/vbulletin/showthread.php?t=111460

* Fri Mar  8 2008 kwizart < kwizart at gmail.com > - 171.06-1
- Update to 171.06 (beta)

* Wed Feb 27 2008 kwizart < kwizart at gmail.com > - 169.12-1
- Update to 169.12

* Wed Feb 20 2008 kwizart < kwizart at gmail.com > - 169.09-5
- Fix debuginfo package creation.
- Add libGLcore.so to the filter list.
- Only requires versioned libGL on x86_64 (no problem on x86).

* Thu Feb 7 2008 Stewart Adam <s.adam AT diffingo DOT com> - 169.09-4
- Filter requires on main package so we don't pull in xorg-x11-drv-nvidia*-libs

* Fri Feb  1 2008 kwizart < kwizart at gmail.com > - 169.09-3
- Remove ldconfig call on the main package 
- Remove some old Obsoletes/Provides
- Move the xorg modules to the main package (not needed for multilib)
- Add Requires versioned libGL.so from the right path
- Uses pkg0 instead of pkg2 for x86_64 (and remove the lib32 from our loop).

* Sun Jan 27 2008 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 169.09-2
- let main package require the libs subpackage

* Wed Jan 23 2008 Stewart Adam <s.adam AT diffingo DOT com> - 169.09-1
- Update to 169.09
- Provides nvidia-glx since we obsolete it
- Make .desktop file to pass desktop-file-validate
- Remove libs-32bit and make a proper multiarch -libs package
- Add empty %%build section

* Thu Dec 27 2007 kwizart < kwizart at gmail.com > - 169.07-4
- Provides libcuda.so.1 since AutoProv is disabled for libs-32bit

* Wed Dec 26 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-3
- Backport changes from testing branch (provide cuda libraries)

* Sun Dec 23 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-2
- Require /usr/lib/libGL.so.1.2 to prevent conflicts
- Do provide libGLcore.so.1

* Sat Dec 22 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-1
- Update to 169.07

* Fri Nov 30 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-6
- Don't provide libGL.so.1 (bz#1741)
- Remove shebang for files that are sourced

* Tue Nov 20 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-5
- Add Requires: which (bz#1662)

* Thu Nov 1 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-4
- Initscript improvements
- Minor bugfixes with scriptlets (don't echo "already disabled" type messages)

* Fri Oct 12 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.19-3
- Initscript should disable when module isn't found (bz#1671)

* Mon Sep 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.19-2
- Fix %%post if clause (bz#1632)
- Disable the DisableGLXRootClipping option

* Thu Sep 20 2007 kwizart < kwizart at gmail.com > - 100.14.19-1
- Update to 100.14.19
- Improve desktop file
- Sync between F7 and FC-6
- Don't replace user env variable

* Thu Jun 21 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.11-1
- Update to 100.14.11

* Fri Jun 15 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.09-2
- F7 SELinux fixes (continued)
- Add a new post scriptlet to remove those legacy-layout udev files

* Sun Jun 10 2007 kwizart < kwizart at gmail.com > - 100.14.09-1
- Update to Final 100.14.09

* Sat Jun 2 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9762-2
- Don't use legacy udev layout (Thanks Finalzone for the workaround)

* Sun May 27 2007 kwizart < kwizart at gmail.com > - 1.0.9762-1
- Update to 1.0.9762

* Sat Apr 28 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9755-3
- Fixes in the config-display (vendor > majorVendor)

* Fri Mar 9 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9755-2
- Fix up scriptlets a little so that 'Driver already enabled|disabled'
  doesn't always appear on install or remove
- Update *-config-display files for majorVendor and not plain vendor

* Thu Mar 8 2007 kwizart < kwizart at gmail.com > - 1.0.9755-1
- Update to 1.0.9755

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-11
- Bump for new tag
- fi to end if!

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-10
- Bump for new tag

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-9
- Standardize all summaries and descriptions with other nvidia and fglrx
  packages
- Standardize initscript and *config-display with other nvidia and fglrx
  packages
- Move paths from nvidia-glx to nvidia
- Start merge with livna-config-display

* Wed Feb 7 2007 kwizart < kwizar at gmail.com > - 1.0.9746-8
- Update SHA1SUM

* Thu Jan 18 2007 Stewart Adam <s.adam AT diffingo DOT com> - 1.0.9746-7
- Fix initscript empty line problem (#1302)
- Fix typo in the readme
- Put in correct sums into SHA1SUM

* Sun Jan 7 2007 kwizart < kwizart at gmail.com > - 1.0.9746-6
- Quick fix double libs-32bit -p /sbin/ldconfig

* Thu Jan 4 2007 kwizart < kwizart at gmail.com > - 1.0.9746-5
- Create the symlink from libwfb.so to libnvidia-wfb.so.x.y.z 
  the xorg driver search for libwfb.so (it do not use the SONAME).
  http://www.nvnews.net/vbulletin/showthread.php?t=83214

* Wed Jan 3 2007 Stewart Adam < s.adam AT diffingo DOT com  - 1.0.9746-4
- Correct mistake in changelog
- add %%verify to /dev nodes (#1324)
- /etc/profile.d/* are sourced, took away exec bit

* Wed Jan 3 2007 Stewart Adam < s.adam AT diffingo DOT com  - 1.0.9746-3
- Make the 32-bit libs run ldconfig in %%postun and %%post steps
- Possible FIXME for future: "E: xorg-x11-drv-nvidia obsolete-not-provided nvidia-glx'

* Thu Dec 28 2006 kwizart < kwizart at gmail.com > - 1.0.9746-2
- Move the libnvidia-wfb.so lib to the Nvidia xorg extension directory.

* Tue Dec 26 2006 kwizart < kwizart at gmail.com > - 1.0.9746-1
- Update to 1.0.9746 (Final).
- Fix symlink of the new lib which soname is libnvidia-wfb.so.1

* Sun Nov 26 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.9742-3
- use Source0 with "pkg0.run" prefix (smaller)
- use Source1 with "pkg2.run" prefix (cotaints the 32bit libs)

* Thu Nov 23 2006 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9742-2
- Fix URL
- Change %%description, as NV30 and below no longer supported
- Update nvidia desktop file

* Mon Nov 20 2006 kwizart < kwiart at gmail.com > - 1.0.9742-1
- Update to release 1.0.9742
- Include libdir/xorg/modules/libnvidia-wfb.so.1.0.9742

* Tue Nov 07 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.9629-1
- update to release 1.0.9629

* Tue Oct 31 2006 Dams <anvil[AT]livna.org> - 1.0.9626-3
- Another nvidia-config-display update to fix dumb modules section

* Tue Oct 24 2006 Dams <anvil[AT]livna.org> - 1.0.9626-2
- Yet another updated nvidia-config-display : importing python modules
  we use is usualy a good idea
- Updated nvidia-config-display

* Sun Oct 22 2006 Stewart Adam <s.adam AT diffingo DOT com> - 1.0.9626-1
- update to release 1.0.9626

* Fri Oct 20 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8776-1
- update to 1.0.8776-1 -- fixes CVE-2006-5379

* Thu Aug 24 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8774-1
- Nvidia added a png for nvidia-settings, for-loop adjusted accordingly
- update to release 1.0.8774

* Wed Aug 09 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-6
- small changes to sync with legacy package
- place nvidia-bug-report.sh in /usr/bin

* Mon Aug 07 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-5
- more minor changes to spacing and general layout

* Fri Aug 04 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-4
- minor changes to spacing, removal of random tabs, re-arrangements
- remove GNOME category from the desktop file

* Thu May 25 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-3
- Obsolete old kmods

* Thu May 24 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-2
- add missing defattr to files section for sub-package libs-32bit

* Wed May 24 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-1
- update to 1.0.8762

* Tue May 16 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8756-3
- Conflict with xorg-x11-drv-fglrx and selinux-policy < 2.2.29-2.fc5
- Ship bug-reporting tool as normal executable and not in %%doc

* Sun May 14 2006 Ville SkyttÃ¤ <ville.skytta at iki.fi> - 1.0.8756-2
- Require nvidia-kmod instead of kmod-nvidia (#970).

* Sat Apr 08 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8756-1
- Update to 8756
- put 32bit libs in their own package

* Wed Mar 29 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8178-9
- make every use of the 'install' command consistent
- tweak nvidia-settings' desktop file slightly

* Thu Mar 23 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8178-8
- switch to using modprobe.d rather than editing modprobe.conf directly

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-7
- ExclusiveArch i386 and not %%{ix86} -- we don't want to build for athlon&co

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-6
- drop unused patches

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-5
- drop 0.lvn

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Wed Feb 08 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.5
- use lib64 in nvidia-config-display on x86-64
- fix path to kernel module in init-script
- add patch from Ville for nvidia-README.Fedora
- match permissions of xorg 7

* Wed Feb 01 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.4
- More fixes

* Tue Jan 31 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.3
- Fix wrong provides

* Mon Jan 30 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.2
- fix path to kernel module in nvidia-glx-init (thx to Dominik 'Rathann'
  Mierzejewski)
- include device files until udev works probably with kernel module

* Sun Jan 22 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.1
- split into packages for userland and kmod
- rename to xorg-x11-drv-nvidia; yum/rpm should use mesa-libGL{,-devel} then in
  the future when seaching for libGL.so{,.1}
- remove kernel-module part
- remove old cruft
- install stuff without Makefile because it forgets mosts a lot of files anyway

* Thu Dec 22 2005 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 0:1.0.8178-0.lvn.2
- change nvidia-glx.sh and nvidia-glx.csh to point to README.txt rather than README
- reference xorg.conf rather than XF86Config in the init script
- improve readability of instructions and comments, fix some typos
- drop epoch, as it seems to be affecting dependencies according to rpmlint
- tweak the nvidia-settings desktop file so it always shows up on the
  menu in the right location
- add the manual pages for nvidia-settings and nvidia-xconfig
- remove header entries from the nvidia-glx files list. they belong in -devel
- fix changelog entries to refer to 7676 not 7176 (though there was a 7176 x86_64
  release prior to 7174)
- add libXvMCNVIDIA.so
- update to 8178

* Wed Dec 07 2005 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 0:1.0.8174-0.lvn.1
- add the manual pages for nvidia-settings and nvidia-xconfig
- install the new nvidia-xconfig utility and associated libs

* Mon Dec 05 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.8174-0.lvn.1
- Update to 8174
- desktop entry now Categories=Settings (#665)
- Ship bug-reporting tool in doc (#588)
- Things from Bug 635, Niko Mirthes (straw) <nmirthes AT gmail DOT com>:
-- avoid changing time stamps on libs where possible
-- only add /etc/modprobe.conf entries if they aren't already there
-- add /etc/modprobe.conf entries one at a time
-- only remove /etc/modprobe.conf entries at uninstall, not during upgrade
-- avoid removing any modprobe.conf entries other than our own
-- match Xorg's install defaults where it makes sense (0444)
-- a few other minor tweaks to the files lists

* Sun Sep 04 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.3
- Conflics with nvidia-glx-legacy
- Integrate some minor correction suggested by Niko Mirthes
  <nmirthes AT gmail DOT com> in #475

* Fri Aug 26 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.2
- Rename src5: nvidia.init to nvidia-glx-init
- Fix correct servicename in nvidia-glx-init
- Run nvidia-glx-init before gdm-early-login; del and readd the script
  during post

* Sun Aug 21 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.1
- Update to 7676
- Lots of cleanup from me and Niko Mirthes <nmirthes AT gmail DOT com>
- add NVreg_ModifyDeviceFiles=0 to modprobe.conf (Niko)
- Drop support for FC2
- Nearly proper Udev-Support with workarounds around FC-Bug 151527

* Fri Jun 17 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.5
- Slight change of modprobe.conf rexexp

* Thu Jun 16 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.4
- Fixed a critical bug in modprobe.conf editing where all lines starting with alias and
  ending with then a word starting with any of the letters n,v,i,d,i,a,N,V,r,e is removed.

* Mon Jun 13 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7174-0.lvn.3
- Adjust kenrnel-module-stuff for FC4
- Ship both x86 and x64 in the SRPM

* Sun Jun 12 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.2
- Only create 16 devices
- Put libXvMCNVIDIA.a in -devel
- Don't remove nvidia options in /etc/modprobe.conf
- Make ld.so.conf file config(noreplace)
- Use same directory permissions as the kernel

* Sat Apr 2 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.1
- New upstream release, 7174

* Wed Mar 30 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.5
- Added x86_64 support patch from Thorsten Leemhuis

* Wed Mar 23 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.4
- Fix kernel module permissions again (644)
- Only create 16 /dev/nvidia* devices, 256 is unnecessary

* Fri Mar 18 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.3
- Fixed kernel-module permissions

* Thu Mar 17 2005 Dams <anvil[AT]livna.org> 0:1.0.7167-0.lvn.2
- Removed provides on kernel-module and kernel-modules

* Sat Mar 05 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.1
- New upstream release 1.0.7167
- Added patch from http://www.nvnews.net/vbulletin/showthread.php?t=47405
- Removed old patch against 2.6.9

* Sat Feb 05 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.7
- Added a number of post-6629 patches from http://www.minion.de/files/1.0-6629
- Fixed permissions of nvidia/nvidia.ko

* Fri Jan 21 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.6
- Fix incorrect MAKDEV behaviour and dependency

* Tue Nov 30 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.4
- Fixed creation of /dev/nvidia* on FC2

* Sat Nov 27 2004 Dams <anvil[AT]livna.org> - 0:1.0.6629-0.lvn.3
- Dont try to print kvariant in description when it's not defined.

* Sun Nov 21 2004 Thorsten Leemhuis <fedora at leemhuis dot info> - 0:1.0.6629-0.lvn.2
- resulting kernel-module package now depends again on /root/vmlinuz-<kernelver>
- Use rpmbuildtags driverp and kernelp

* Sat Nov 06 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.1
- New upstream version, 1.0-6629
- Build without kernel-module-devel by default

* Fri Oct 29 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.6
- Make n-c-display handle misc problems in a better way
- Fixed wrong icon file name in .desktop file
- Re-added the mysteriously vanished sleep line in the init script
  when kernel module wasn't present

* Fri Oct 22 2004 Thorsten Leemhuis <fedora at leemhuis dot info> - 0:1.0.6111-0.lvn.5
- Use fedora-kmodhelper in the way ntfs or ati-fglrx use it
- Allow rpm to strip the kernel module. Does not safe that much space ATM but
  might be a good idea
- Allow to build driver and kernel-module packages independent of each other
- Some minor spec-file changes

* Thu Oct 21 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.4
- udev fixes
- Incorporated fix for missing include line in ld.so.conf from ati-fglrx spec (T Leemhuis)

* Sun Sep 19 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.3
- Remove FC1/kernel 2.4 compability
- Rename srpm to nvidia-glx
- Build with kernel-module-devel

* Sun Aug 15 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.2
- Restore ldsoconfd macro
- Disable autoamtic removal of scripted installation for now; needs testing

* Sat Aug 14 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.1
- Upstream release 6111
- Fixed init script (again)

* Tue Aug  3 2004 Dams <anvil[AT]livna.org> 0:1.0.6106-0.lvn.4
- ld.so.conf.d directory detected by spec file
- Using nvidialibdir in nvidia-glx-devel files section
- Got rid of yarrow and tettnang macros
- libGL.so.1 symlink in tls directory always present

* Mon Jul 19 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.3
- Fixed script bug that would empty prelink.conf
- Added symlink to non-tls libGL.so.1 on FC1

* Tue Jul 13 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.3
- Updated init script to reflect name change -xfree86 -> -display

* Mon Jul 12 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.2
- Fixed backup file naming

* Sun Jul 11 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.1
- Restore working macros
- Always package the gui tool

* Sun Jul 11 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2
- Renamed nvidia-config-xfree86 to nvidia-config-display
- Fixed symlinks
- Use ld.so.conf.d on FC2
- Remove script installation in pre
- Use system-config-display icon for nvidia-settings
- 2 second delay in init script when kernel module not found
- Make nvidia-config-display fail more gracefully
- Add blacklist entry to prelink.conf on FC1

* Mon Jul 05 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.1
- New upstream release
- First attempt to support FC2
- Dropped dependency on XFree86

* Mon Feb 09 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.5336-0.lvn.3
- Use pkg0

* Sun Feb 08 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.5336-0.lvn.2
- New Makefile variable SYSSRC to point to kernel sources.
- kmodhelper fixes.

* Fri Jan 30 2004 Keith G. Robertson-Turner <nvidia-devel[AT]genesis-x.nildram.co.uk> 0:1.0.5336-0.lvn.1
- New upstream release
- Removed (now obsolete) kernel-2.6 patch
- Install target changed upstream, from "nvidia.o" to "module"
- Linked nv/Makefile.kbuild to (now missing) nv/Makefile

* Sun Jan 25 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.18
- Updated nvidia-config-display
- Now requiring pyxf86config

* Mon Jan 19 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.17
- Added nvidiasettings macro to enable/disable gui packaging

* Mon Jan 19 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.16
- Updated minion.de patches
- Added some explicit requires
- Test nvidia-config-xfree86 presence in kernel-module package
  scriptlets

* Mon Jan 12 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.15
- Updated Readme.fedora
- nvidia-glx-devel package

* Sat Jan  3 2004 Dams <anvil[AT]livna.org> 0:1.0.5328-0.lvn.14
- Hopefully fixed kernel variant thingy

* Fri Jan  2 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.13
- Support for other kernel variants (bigmem, etc..)
- Changed URL in Source0

* Tue Dec 30 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.13
- Dropped nvidia pkgX information in release tag.

* Tue Dec 30 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.12.pkg0
- Renamed kernel module package in a kernel-module-nvidia-`uname -r` way
- Using fedora.us kmodhelper for kernel macro
- Using nvidia pkg0 archive

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.11.pkg1
- kernel-module-nvidia package provides kernel-module
- We wont own devices anymore. And we wont re-create them if they are
  already present

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.10.pkg1
- Yet another initscript update. Really.
- Scriptlets updated too

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.9.pkg1
- Fixed alias in modprobe.conf for 2.6

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.8.pkg1
- Another initscript update

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.7.pkg1
- kernel module requires kernel same kversion
- initscript updated again
- Dont conflict, nor obsolete XFree86-Mesa-libGL. Using ld.so.conf to
  make libGL from nvidia first found. Hope Mike Harris will appreciate.

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.6.pkg1
- kernel-module-nvidia requires kernel same version-release

* Sat Dec 20 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.6.pkg1
- Updated initscript

* Fri Dec 19 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.5.pkg1
- lvn repository tag

* Fri Dec 19 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.5.pkg1
- Added initscript to toggle nvidia driver according to running kernel
  and installed kernel-module-nvidia packages
- Updated scriptlets

* Thu Dec 18 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.4.pkg1
- Arch detection
- Url in patch0

* Tue Dec 16 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.3.pkg1
- Desktop entry for nvidia-settings
- s/kernel-module-{name}/kernel-module-nvidia
- nvidia-glx doesnt requires kernel-module-nvidia-driver anymore
- Using modprobe.conf for 2.6 kernel
- Hopefully fixed symlinks

* Mon Dec 15 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.2.pkg1
- Building kernel module for defined kernel
- kernel module for 2.6 is nvidia.ko
- Patch not to install kernel module on make install
- Updated patch for 2.6
- depmod in scriptlet for defined kernel
- nvidia-glx conflicting XFree86-Mesa-libGL because we 0wn all its
  symlink now
- Dont override libGL.so symlink because it belongs to XFree86-devel
- Added nvidia 'pkgfoo' info to packages release
- Spec file cleanup

* Fri Dec 12 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4620-0.fdr.2
- Fixed repairing of a link in post-uninstall
- Obsolete Mesa instead of Conflict with it, enables automatic removal.

* Mon Dec 08 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4620-0.fdr.1
- Added support for 2.6 kernels
- Cleaned up build section, removed the need for patching Makefiles.
- Added missing BuildReq gcc32
- Don't package libs twice, only in /usr/lib/tls/nvidia
- Made config cript executable and put it into /usr/sbin
- Moved kernel module to kernel/drivers/video/nvidia/
- Fixed libGL.so and libGLcore.so.1 links to allow linking against OpenGL libraries

* Mon Dec 08 2003 Keith G. Robertson-Turner <nvidia-devel at genesis-x.nildram.co.uk> - 0:1.0.4620-0.fdr.0
- New beta 4620 driver
- New GUI control panel
- Some minor fixes

* Thu Nov 20 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.10.1
- Finally fixed SMP builds.

* Wed Nov 19 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.9
- Don't make nvidia-glx depend on kernel-smp

* Tue Nov 18 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.8
- Some build fixes

* Tue Nov 11 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.7
- Added CC=gcc32
- Fixed upgrading issue
- Added driver switching capabilities to config script.

* Fri Nov 07 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.4
- Added conflict with XFree86-Mesa-libGL.
- Disabled showing of the README.Fedora after installation.

* Sun Oct 12 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.3
- Added NVidia configuration script written in Python.
- Some cleanup of files section
- For more info, see https://bugzilla.fedora.us/show_bug.cgi?id=402

* Tue Jul 08 2003 Andreas Bierfert (awjb) <andreas.bierfert[AT]awbsworld.de> - 0:1.0.4363-0.fdr.2
- renamed /sbin/makedevices.sh /sbin/nvidia-makedevices.sh ( noticed by
  Panu Matilainen )
- Fixed name problem
* Sun Jun 22 2003 Andreas Bierfert (awjb) <andreas.bierfert[AT]awbsworld.de> - 0:1.0.4363-0.fdr.1
- Initial RPM release, still some ugly stuff in there but should work...
