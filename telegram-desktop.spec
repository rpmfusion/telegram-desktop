# Enable or disable build with GTK support...
%bcond_without gtk3

# Enable or disable build using clang instead of gcc...
%if 0%{?fedora} && 0%{?fedora} == 31
%bcond_without clang
%else
%bcond_with clang
%endif

# Telegram Desktop's constants...
%global appname tdesktop
%global apiid 208164
%global apihash dfbe1bc42dc9d20507e17d1814cc2f0a
%global upstreambase https://github.com/telegramdesktop

# Git revision of crl...
%global commit1 52baf11aaeb7f5ea6955a438abaa1aee4c4308d8
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Git revision of patched rlottie...
%global commit2 d08a03b6508b390af20491f2dbeee3453594afc8
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})

# Decrease debuginfo verbosity to reduce memory consumption...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/-Qunused-arguments -Wno-unknown-warning-option/')
%endif

Summary: Telegram Desktop official messaging app
Name: telegram-desktop
Version: 1.8.3
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * S0 (Telegram Desktop) - GPLv3+ with OpenSSL exception -- main source;
# * S1 (crl) - GPLv3+ -- build-time dependency;
# * S2 (rlottie) - LGPLv2+ -- static dependency;
# * P0 (qt_functions.cpp) - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv3
URL: %{upstreambase}/%{appname}

%if 0%{?fedora} && 0%{?fedora} < 31
ExclusiveArch: i686 x86_64
%else
ExclusiveArch: x86_64
%endif

# Source files...
Source0: %{url}/archive/v%{version}.tar.gz#/%{appname}-%{version}.tar.gz
Source1: %{upstreambase}/crl/archive/%{commit1}.tar.gz#/crl-%{shortcommit1}.tar.gz
Source2: https://github.com/john-preston/rlottie/archive/%{commit2}.tar.gz#/rlottie-%{shortcommit2}.tar.gz

# Downstream patches...
Patch0: %{name}-build-fixes.patch
Patch1: %{name}-system-fonts.patch
Patch2: %{name}-unbundle-minizip.patch

%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
Requires: qt5-qtimageformats%{?_isa}
Requires: hicolor-icon-theme
Requires: open-sans-fonts

# Telegram Desktop require patched version of rlottie since 1.8.0.
# Pull Request pending: https://github.com/Samsung/rlottie/pull/252
Provides: bundled(rlottie) = 0~git%{shortcommit2}

# Compilers and tools...
BuildRequires: desktop-file-utils
BuildRequires: libappstream-glib
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gyp

# Development packages for Telegram Desktop...
BuildRequires: guidelines-support-library-devel >= 1.0.0
BuildRequires: mapbox-variant-devel >= 0.3.6
BuildRequires: qt5-qtbase-private-devel
BuildRequires: libtgvoip-devel >= 2.4.4
BuildRequires: ffmpeg-devel >= 3.1
BuildRequires: openal-soft-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: libstdc++-devel
BuildRequires: range-v3-devel
BuildRequires: openssl-devel
BuildRequires: xxhash-devel
BuildRequires: json11-devel
BuildRequires: glib2-devel
BuildRequires: opus-devel
BuildRequires: lz4-devel
BuildRequires: xz-devel
BuildRequires: python3

%if %{with gtk3}
Recommends: libappindicator-gtk3%{?_isa}
BuildRequires: libappindicator-devel
BuildRequires: gtk3-devel
BuildRequires: dee-devel
Requires: gtk3%{?_isa}
%endif

%if %{with clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
%endif

%if 0%{?fedora} && 0%{?fedora} >= 30
BuildRequires: minizip-compat-devel
%else
BuildRequires: minizip-devel
%endif

%description
Telegram is a messaging app with a focus on speed and security, it’s super
fast, simple and free. You can use Telegram on all your devices at the same
time — your messages sync seamlessly across any number of your phones,
tablets or computers.

With Telegram, you can send messages, photos, videos and files of any type
(doc, zip, mp3, etc), as well as create groups for up to 50,000 people or
channels for broadcasting to unlimited audiences. You can write to your
phone contacts and find people by their usernames. As a result, Telegram is
like SMS and email combined — and can take care of all your personal or
business messaging needs.

%prep
# Unpacking Telegram Desktop source archive...
%autosetup -n %{appname}-%{version} -p1

# Unpacking crl...
pushd Telegram/ThirdParty
    rm -rf crl
    tar -xf %{SOURCE1}
    mv crl-%{commit1} crl
popd

# Unpacking patched rlottie...
pushd Telegram/ThirdParty
    rm -rf rlottie
    tar -xf %{SOURCE2}
    mv rlottie-%{commit2} rlottie
popd

%build
# Setting build definitions...
%if %{without gtk3}
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_GTK_INTEGRATION,'
%endif
%if 0%{?fedora} && 0%{?fedora} < 30
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_OPENAL_EFFECTS,'
%endif
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_AUTOUPDATE,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_REGISTER_CUSTOM_SCHEME,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_DESKTOP_FILE_GENERATION,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_DISABLE_CRASH_REPORTS,'
TDESKTOP_BUILD_DEFINES+='TDESKTOP_LAUNCHER_FILENAME=%{name}.desktop,'

# Generating cmake script using GYP...
pushd Telegram/gyp
    gyp --depth=. --generator-output=../.. -Goutput_dir=out -Dapi_id=%{apiid} -Dapi_hash=%{apihash} -Dbuild_defines=$TDESKTOP_BUILD_DEFINES Telegram.gyp --format=cmake
popd

# Patching generated cmake script...
LEN=$(($(wc -l < out/Release/CMakeLists.txt) - 2))
sed -i "$LEN r Telegram/gyp/CMakeLists.inj" out/Release/CMakeLists.txt

# Building Telegram Desktop using cmake...
pushd out/Release
    %cmake \
%if %{with clang}
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_AR=%{_bindir}/llvm-ar \
    -DCMAKE_RANLIB=%{_bindir}/llvm-ranlib \
    -DCMAKE_LINKER=%{_bindir}/llvm-ld \
    -DCMAKE_OBJDUMP=%{_bindir}/llvm-objdump \
    -DCMAKE_NM=%{_bindir}/llvm-nm \
%else
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm \
%endif
    .
    %make_build
popd

%install
# Installing executables...
%{__mkdir_p} "%{buildroot}%{_bindir}"
%{__install} -m 0755 -p out/Release/Telegram "%{buildroot}%{_bindir}/%{name}"

# Installing desktop shortcut...
%{__mv} lib/xdg/telegramdesktop.desktop lib/xdg/%{name}.desktop
desktop-file-install --dir="%{buildroot}%{_datadir}/applications" lib/xdg/%{name}.desktop

# Installing icons...
for size in 16 32 48 64 128 256 512; do
    dir="%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps"
    %{__install} -d "$dir"
    %{__install} -m 0644 -p Telegram/Resources/art/icon${size}.png "$dir/%{name}.png"
done

# Installing appdata for Gnome Software...
%{__install} -d %{buildroot}%{_metainfodir}
%{__install} -m 0644 -p lib/xdg/telegramdesktop.appdata.xml %{buildroot}%{_metainfodir}/%{name}.appdata.xml

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{name}.appdata.xml

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_metainfodir}/%{name}.appdata.xml

%changelog
* Fri Sep 06 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.3-1
- Updated to 1.8.3.
- Switched back to GCC compiler (except Fedora 31 due to beta freeze).

* Thu Aug 22 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.2-2
- Removed kde subpackage.

* Tue Aug 20 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.2-1
- Updated to 1.8.2.

* Sat Aug 10 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.1-1
- Updated to 1.8.1.

* Fri Aug 09 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.0-1
- Updated to 1.8.0.

* Fri Jul 19 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.15-1
- Updated to 1.7.15 (beta).

* Tue Jul 09 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.14-1
- Updated to 1.7.14.

* Fri Jul 05 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.11-1
- Updated to 1.7.11 (beta).

* Wed Jul 03 2019 Vasiliy Glazov <vascom2@gmail.com> - 1.7.10-2
- Rebuild for new Qt5

* Mon Jun 24 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.10-1
- Updated to 1.7.10.

* Mon Jun 24 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.9-1
- Updated to 1.7.9.

* Tue Jun 18 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.8-1
- Updated to 1.7.8 (beta).

* Mon Jun 10 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.7-1
- Updated to 1.7.7.

* Fri Jun 07 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.6-1
- Updated to 1.7.6 (beta).

* Sat Jun 01 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.3-1
- Updated to 1.7.3.

* Wed May 29 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.1-1
- Updated to 1.7.1 (beta).

* Sat May 18 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.0-2
- Switched to clang as a temporary workaround on Fedora 30+.
- Disabled LTO optimizations.

* Thu May 09 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.7.0-1
- Updated to 1.7.0.

* Tue Apr 16 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.7-2
- Rebuilt due to Qt 5.12.1 update.

* Sat Apr 13 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.7-1
- Updated to 1.6.7.

* Thu Apr 11 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.6-1
- Updated to 1.6.6 (beta).

* Sat Apr 06 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.5-1
- Updated to 1.6.5 (beta).

* Tue Mar 26 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.3-1
- Updated to 1.6.3.

* Sun Mar 24 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.2-1
- Updated to 1.6.2.

* Wed Mar 20 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.1-1
- Updated to 1.6.1.

* Mon Mar 18 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.6.0-1
- Updated to 1.6.0.

* Fri Mar 15 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.18-1
- Updated to 1.5.18 (beta).

* Wed Mar 13 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.17-1
- Updated to 1.5.17 (beta).

* Tue Mar 12 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.16-1
- Updated to 1.5.16 (beta).

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.5.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Feb 13 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.15-1
- Updated to 1.5.15.

* Tue Feb 12 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.13-1
- Updated to 1.5.13.

* Sun Feb 10 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.12-1
- Updated to 1.5.12.

* Fri Feb 01 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.11-1
- Updated to 1.5.11.
- Enabled LTO optimizations.

* Fri Feb 01 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.10-1
- Updated to 1.5.10.

* Mon Jan 21 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.8-1
- Updated to 1.5.8.

* Fri Jan 11 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.7-1
- Updated to 1.5.7 (beta).

* Fri Dec 28 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.6-1
- Updated to 1.5.6 (beta).

* Thu Dec 27 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.5-1
- Updated to 1.5.5 (beta).

* Mon Dec 24 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.4-1
- Updated to 1.5.4.

* Sun Dec 23 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.3-1
- Updated to 1.5.3.

* Fri Dec 14 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.2-1
- Updated to 1.5.2.

* Tue Dec 11 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.1-1
- Updated to 1.5.1.

* Mon Dec 10 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.5.0-1
- Updated to 1.5.0.

* Wed Dec 05 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.8-1
- Updated to 1.4.8 (beta).

* Sat Nov 10 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.7-1
- Updated to 1.4.7 (beta).

* Thu Nov 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.5-1
- Updated to 1.4.5 (beta).

* Wed Oct 17 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.4-1
- Updated to 1.4.4 (beta).

* Sat Oct 13 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.3-1
- Updated to 1.4.3.

* Wed Oct 10 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.2-2
- Backported patch with crash fix on logout.

* Tue Oct 09 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.2-1
- Updated to 1.4.2.

* Fri Sep 28 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.4.0-1
- Updated to 1.4.0.

* Wed Sep 26 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.17-1
- Updated to 1.3.17 (alpha).

* Wed Sep 05 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.16-1
- Updated to 1.3.16 (alpha).

* Sat Sep 01 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.15-1
- Updated to 1.3.15 (alpha).

* Tue Aug 28 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.14-1
- Updated to 1.3.14.

* Mon Aug 27 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.13-1
- Updated to 1.3.13.

* Sat Aug 04 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.12-1
- Updated to 1.3.12 (alpha).

* Thu Aug 02 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.11-1
- Updated to 1.3.11 (alpha).

* Mon Jul 30 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.10-3
- Rebuild for libtgvoip update and issue with binutils.

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.3.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jul 13 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.10-1
- Updated to 1.3.10.

* Mon Jul 02 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.9-2
- Rebuild for libtgvoip update.

* Fri Jun 29 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.9-1
- Updated to 1.3.9.

* Sun Jun 24 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.8-1
- Updated to 1.3.8.

* Mon Jun 11 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.7-1
- Updated to 1.3.7.

* Mon Jun 11 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.6-1
- Updated to 1.3.6 (alpha).

* Sat Jun 09 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.5-1
- Updated to 1.3.5 (alpha).

* Fri Jun 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.4-1
- Updated to 1.3.4 (alpha).

* Thu Jun 07 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.3-1
- Updated to 1.3.3 (alpha).

* Tue Jun 05 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.1-1
- Updated to 1.3.1 (alpha).

* Fri Jun 01 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.3.0-1
- Updated to 1.3.0.

* Sat May 26 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.24-1
- Updated to 1.2.24 (alpha).

* Fri May 25 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.23-1
- Updated to 1.2.23 (alpha).

* Thu May 24 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.22-1
- Updated to 1.2.22 (alpha).

* Sat May 19 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.21-2
- Updated to 1.2.21 (alpha).

* Sun May 13 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.20-1
- Updated to 1.2.20 (alpha).

* Tue May 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.19-1
- Updated to 1.2.19 (alpha).

* Sat May 05 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.18-1
- Updated to 1.2.18 (alpha).

* Mon Apr 09 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.17-2
- Added custom API tokens.

* Sun Apr 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.17-1
- Updated to 1.2.17.

* Sun Apr 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.16-1
- Updated to 1.2.16.

* Mon Mar 26 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.15-1
- Updated to 1.2.15.

* Thu Mar 22 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.14-1
- Updated to 1.2.14.

* Wed Mar 21 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.13-1
- Updated to 1.2.13 (alpha).

* Mon Mar 12 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.12-1
- Updated to 1.2.12 (alpha).

* Sat Mar 10 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.11-1
- Updated to 1.2.11 (alpha).

* Fri Mar 09 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.10-1
- Updated to 1.2.10 (alpha).

* Thu Mar 08 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.9-1
- Updated to 1.2.9 (alpha).

* Wed Jan 03 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.8-1
- Updated to 1.2.8 (alpha).

* Mon Jan 01 2018 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.7-1
- Updated to 1.2.7 (alpha).

* Sat Dec 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.6-1
- Updated to 1.2.6.

* Fri Dec 29 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.5-1
- Updated to 1.2.5 (alpha).

* Wed Dec 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.4-1
- Updated to 1.2.4 (alpha).

* Sun Dec 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.3-1
- Updated to 1.2.3 (alpha).

* Tue Dec 12 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.1-1
- Updated to 1.2.1.

* Sun Dec 10 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.2.0-1
- Updated to 1.2.0.

* Sat Dec 09 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.29-1
- Updated to 1.1.29 (alpha).

* Sat Dec 09 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.28-1
- Updated to 1.1.28 (alpha).

* Wed Dec 06 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.27-1
- Updated to 1.1.27 (alpha).

* Sat Dec 02 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.26-1
- Updated to 1.1.26 (alpha).

* Fri Dec 01 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.25-1
- Updated to 1.1.25 (alpha).

* Thu Nov 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.24-1
- Updated to 1.1.24 (alpha).

* Sat Nov 18 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.23-4
- Rebuild against libtgvoip 1.0.1.

* Fri Nov 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.23-3
- Rebuild for Qt 5.9 major update. Backported upstream patches.

* Tue Oct 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.1.23-2
- Rebuild for ffmpeg update

* Wed Sep 06 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.23-1
- Updated to 1.1.23.

* Mon Sep 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.22-1
- Updated to 1.1.22.

* Mon Sep 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.21-1
- Updated to 1.1.21.

* Fri Aug 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.19-2
- Moved VoIP library into a separate package.

* Wed Aug 02 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.19-1
- Updated to 1.1.19.

* Thu Jul 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.18-1
- Updated to 1.1.18.

* Thu Jul 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.17-1
- Updated to 1.1.17.

* Sun Jul 23 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.15-1
- Updated to 1.1.15.

* Wed Jul 19 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.14-1
- Updated to 1.1.14 (alpha).

* Fri Jul 14 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.13-1
- Updated to 1.1.13 (alpha).

* Wed Jul 12 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.12-1
- Updated to 1.1.12 (alpha).

* Sun Jul 09 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.11-2
- Fixed some small bugs.

* Fri Jul 07 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.11-1
- Updated to 1.1.11 (alpha).

* Tue Jul 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.10-1
- Updated to 1.1.10.

* Fri Jun 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.9-1
- Updated to 1.1.9.

* Wed May 31 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.7-1
- Updated to 1.1.7.

* Sat May 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.6-1
- Updated to 1.1.6 (alpha).

* Fri May 26 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.5-1
- Updated to 1.1.5 (alpha).

* Thu May 25 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.4-1
- Updated to 1.1.4 (alpha).

* Wed May 24 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.3-1
- Updated to 1.1.3 (alpha).

* Thu May 18 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.2-1
- Updated to 1.1.2.

* Wed May 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.1-1
- Updated to 1.1.1 (alpha).

* Tue May 16 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.0-3
- Backported patch with crash fixes.

* Mon May 15 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.0-2
- Restored russian locale.

* Sun May 14 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.1.0-1
- Updated to 1.1.0.

* Sun May 14 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.38-2
- Fixed rpmlint errors and warnings. Set soname for shared library.

* Sat May 13 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.38-1
- Updated to 1.0.38 (alpha).

* Wed May 10 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.37-1
- Updated to 1.0.37 (alpha).

* Wed May 10 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.36-1
- Updated to 1.0.36 (alpha).

* Sun Apr 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.35-1
- Updated to 1.0.35 (alpha).

* Sun Apr 30 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.0.34-2
- Rebuild for ffmpeg update

* Mon Apr 24 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.34-1
- Updated to 1.0.34 (alpha).

* Sun Apr 16 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.33-1
- Updated to 1.0.33 (alpha).

* Thu Apr 13 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.32-1
- Updated to 1.0.32 (alpha).

* Tue Apr 11 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.31-1
- Updated to 1.0.31 (alpha).

* Wed Apr 05 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.29-1
- Updated to 1.0.29.

* Tue Apr 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.28-1
- Updated to 1.0.28 (alpha).

* Mon Apr 03 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.27-3
- Strip binary into debuginfo subpackage.

* Sat Apr 01 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.27-2
- Built against system Qt.

* Fri Mar 31 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.27-1
- Updated to 1.0.27.

* Thu Mar 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.26-3
- Fixed build under GCC 7.0.

* Thu Mar 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.26-2
- Backported patch to fix build under Fedora 26+.

* Thu Mar 30 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.26-1
- Updated to 1.0.26.

* Wed Mar 22 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.25-1
- Updated to 1.0.25 (alpha).

* Sun Mar 19 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.24-1
- Updated to 1.0.24 (alpha).

* Fri Mar 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.23-2
- Added additional russian locale.

* Wed Mar 15 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.23-1
- Updated to 1.0.23 (alpha).

* Mon Mar 13 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.22-1
- Updated to 1.0.22 (alpha).

* Sat Mar 11 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.21-1
- Updated to 1.0.21 (alpha).
- Updated GSL build stage. Added Variant to build.

* Thu Mar 09 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.20-1
- Updated to 1.0.20 (alpha).

* Wed Mar 08 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.19-1
- Updated to 1.0.19 (alpha).

* Sat Mar 04 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.18-2
- Fixed build of latest commits. Added GSL support.

* Thu Mar 02 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.18-1
- Updated to 1.0.18 (alpha).

* Tue Feb 28 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.17-1
- Updated to 1.0.17 (alpha).

* Mon Feb 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.15-1
- Updated to 1.0.15 (alpha).

* Tue Feb 21 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.14-1
- Updated to 1.0.14.

* Mon Feb 20 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.13-1
- Updated to 1.0.13.
- Added changelog.txt to documents.

* Sun Feb 19 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.12-1
- Updated to 1.0.12.

* Fri Feb 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.11-1
- Updated to 1.0.11 (alpha).

* Sun Feb 12 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.9-1
- Updated to 1.0.9 (alpha).
- Updated GYP, Breakpad and LSS to latest commits.

* Thu Feb 02 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.6-2
- Backported QTBUG-56514 patch to fix building under GCC 7.0.

* Wed Feb 01 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.6-1
- Updated to 1.0.6.

* Fri Jan 27 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.3-1
- Updated to 1.0.3 (alpha).

* Thu Jan 19 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.2-1
- Updated to 1.0.2.

* Tue Jan 17 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.1-1
- Updated to 1.0.1.

* Thu Jan 12 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 1.0.0-1
- Updated to 1.0.0.

* Wed Jan 11 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.27-1
- Updated to 0.10.27 (alpha).

* Sat Jan 07 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.26-1
- Updated to 0.10.26 (alpha).

* Thu Jan 05 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.25-1
- Updated to 0.10.25 (alpha). Added patch to build with GCC 6.3.1.

* Mon Jan 02 2017 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.23-1
- Updated to 0.10.23 (alpha). Updated externals to latest commits.

* Tue Dec 20 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.20-1
- Updated to 0.10.20.

* Sun Oct 30 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.19-2
- Fixed build under Fedora Rawhide (26).

* Tue Oct 25 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.19-1
- Updated to 0.10.19.

* Fri Oct 21 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.16-2
- Use specified revisions of 3rd-party libraries.

* Thu Oct 20 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.16-1
- Updated to 0.10.16.

* Wed Oct 19 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.15-1
- Updated to 0.10.15.

* Tue Oct 18 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.14-1
- Updated to 0.10.14.

* Sat Oct 08 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.11-3
- GYP will now export correct build flags for project.

* Sat Oct 08 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.11-2
- Will use configure macro to export correct build flags.

* Mon Oct 03 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.11-1
- Updated to 0.10.11.

* Wed Sep 21 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.7-1
- Updated to 0.10.7.

* Tue Sep 20 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.6-3
- Added new patch to build project using systemwide cmake.

* Sat Sep 17 2016 Vitaly Zaitsev <vitaly@easycoding.org> - 0.10.6-2
- Created new SPEC.
- Added installation of tg protocol and mime-handler.

* Wed Sep 14 2016 Arkady L. Shane <ashejn@russianfedora.pro> 0.10.6-1
- update to 0.10.6

* Mon Aug  8 2016 Arkady L. Shane <ashejn@russianfedora.pro> 0.10.1-2
- added appdata file

* Mon Aug  8 2016 Arkady L. Shane <ashejn@russianfedora.pro> 0.10.1-1
- update to 0.10.1

* Thu Aug  4 2016 Arkady L. Shane <ashejn@russianfedora.pro> 0.10.0-1
- update to 0.10.0

* Mon Jun 27 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.56-1.R
- update to 0.9.56

* Thu Jun 16 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.51-1.R
- update to 0.9.51

* Wed May 25 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.49-1.R
- update to 0.9.49

* Wed May 11 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.48-1.R
- update to 0.9.48

* Thu Apr 14 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.42-1.R
- update to 0.9.42

* Wed Apr 13 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.41-1.R
- update to 0.9.41

* Tue Apr  5 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.40-1.R
- update to 0.9.40

* Wed Mar 16 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.33-1.R
- update to 0.9.33

* Tue Mar 15 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.32-1.R
- update to 0.9.32

* Mon Feb 29 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.28-1.R
- update to 0.9.28

* Tue Feb 23 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.26-1.R
- update to 0.9.26

* Wed Feb 17 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.24-1.R
- update to 0.9.18

* Sun Jan 10 2016 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.18-1.R
- update to 0.9.18

* Thu Dec 10 2015 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.15-1.R
- update to 0.9.15

* Thu Nov 26 2015 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.13-1.R
- update to 0.9.13

* Fri Nov 13 2015 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.10-1.R
- update to 0.9.10

* Tue Oct 27 2015 Arkady L. Shane <ashejn@russianfedora.pro> - 0.9.6-1.R
- clean up spec
- update to 0.9.6

* Mon Aug 03 2015 rommon <rommon@t-online.de> - 0.8.45-1
- update to new version

* Sat Jul 18 2015 rommon <rommon@t-online.de> - 0.8.38-1
- update to new version

* Fri Jun 26 2015 rommon <rommon@t-online.de> - 0.8.32-1
- update to new version
- rename from telegram to telegram-desktop

* Tue Jun 9 2015 rommon <rommon@t-online.de> - 0.8.24-1
- update to new version

* Fri May 1 2015 rommon <rommon@t-online.de> - 0.8.11-1
- update to new version

* Mon Apr 27 2015 rommon <rommon@t-online.de> - 0.8.7-1
- update to new version

* Mon Apr 27 2015 rommon <rommon@t-online.de> - 0.8.4-5
- fix icon permissions

* Fri Apr 24 2015 rommon <rommon@t-online.de> - 0.8.4-4
- fix desktop file

* Tue Apr 21 2015 rommon <rommon@t-online.de> - 0.8.4-3
- changed desktop file

* Tue Apr 21 2015 rommon <rommon@t-online.de> - 0.8.4-2
- adaption for 32/64 bit builds

* Tue Apr 21 2015 rommon <rommon@t-online.de> - 0.8.4-1
- initial package
