%undefine __cmake_in_source_build
%define _lto_cflags %{nil}

# Build conditionals (with - OFF, without - ON)...
%bcond_with rlottie
%bcond_without webrtc
%bcond_with gtk3
%bcond_with clang

# F33+ has some issues with LTO: https://bugzilla.redhat.com/show_bug.cgi?id=1880290
%if 0%{?fedora} && 0%{?fedora} >= 33
%bcond_with ipo
%else
%bcond_without ipo
%endif

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# Git revision of WebRTC...
%global commit1 7a9d4bd6d9a147d15e3c8fa818a716c31f65606a
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%if 0%{?fedora} && 0%{?fedora} >= 33
%global toolchain clang
%else
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/ -Qunused-arguments -Wno-unknown-warning-option -Wno-deprecated-declarations/')
%endif
%endif

# Decrease debuginfo verbosity to reduce memory consumption...
%ifarch x86_64
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%else
%global optflags %(echo %{optflags} | sed 's/-g /-g2 /')
%endif

Name: telegram-desktop
Version: 2.4.3
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPLv3+ with OpenSSL exception -- main tarball;
# * tg_owt - BSD -- static dependency;
# * rlottie - LGPLv2+ -- static dependency;
# * qt_functions.cpp - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app

Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}-full.tar.gz
Source1: https://github.com/desktop-app/tg_owt/archive/%{commit1}/owt-%{shortcommit1}.tar.gz

# Telegram Desktop require more than 8 GB of RAM on linking stage.
# Disabling all low-memory architectures.
ExclusiveArch: x86_64

# Telegram Desktop require exact version of Qt due to Qt private API usage.
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
Requires: qt5-qtimageformats%{?_isa}
Requires: hicolor-icon-theme
Requires: open-sans-fonts

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Telegram Desktop require patched version of rlottie since 1.8.0.
# Pull Request pending: https://github.com/Samsung/rlottie/pull/252
%if %{with rlottie}
BuildRequires: rlottie-devel
%else
Provides: bundled(rlottie) = 0~git
%endif

# Telegram Desktop require patched version of lxqt-qtplugin.
# Pull Request pending: https://github.com/lxqt/lxqt-qtplugin/pull/52
Provides: bundled(lxqt-qtplugin) = 0.14.0~git

# Compilers and tools...
BuildRequires: desktop-file-utils
BuildRequires: libappstream-glib
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: gcc

# Development packages for Telegram Desktop...
BuildRequires: guidelines-support-library-devel >= 3.0.1
BuildRequires: qt5-qtbase-private-devel
BuildRequires: libtgvoip-devel >= 2.4.4
BuildRequires: range-v3-devel >= 0.10.0
BuildRequires: libqrcodegencpp-devel
BuildRequires: minizip-compat-devel
BuildRequires: qt5-qtwayland-devel
BuildRequires: ffmpeg-devel >= 3.1
BuildRequires: dbusmenu-qt5-devel
BuildRequires: openal-soft-devel
BuildRequires: qt5-qtbase-static
BuildRequires: qt5-qtbase-devel
BuildRequires: libstdc++-devel
BuildRequires: expected-devel
BuildRequires: hunspell-devel
BuildRequires: openssl-devel
BuildRequires: wayland-devel
BuildRequires: xxhash-devel
BuildRequires: json11-devel
BuildRequires: ninja-build
BuildRequires: glib2-devel
BuildRequires: opus-devel
BuildRequires: libatomic
BuildRequires: lz4-devel
BuildRequires: xz-devel
BuildRequires: python3

%if %{with webrtc}
BuildRequires: pulseaudio-libs-devel
BuildRequires: libjpeg-turbo-devel
BuildRequires: alsa-lib-devel
BuildRequires: yasm

Provides: bundled(tg_owt) = 0~git%{shortcommit1}
Provides: bundled(openh264) = 0~git
Provides: bundled(abseil-cpp) = 0~git
Provides: bundled(libsrtp) = 0~git
Provides: bundled(libvpx) = 0~git
Provides: bundled(libyuv) = 0~git
Provides: bundled(pffft) = 0~git
Provides: bundled(rnnoise) = 0~git
Provides: bundled(usrsctp) = 0~git
%endif

%if %{with clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
%endif

%if %{with gtk3}
BuildRequires: gtk3-devel
Requires: gtk3%{?_isa}
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
%autosetup -n %{appname}-%{version}-full -p1

# Unpacking WebRTC...
%if %{with webrtc}
tar -xf %{SOURCE1}
mv tg_owt-%{commit1} tg_owt
%endif

# Unbundling libraries...
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,libdbusmenu-qt,libqtxdg,libtgvoip,lxqt-qtplugin,lz4,materialdecoration,minizip,nimf,qt5ct,range-v3,xxHash}

# Unbundling rlottie if build against packaged version...
%if %{with rlottie}
rm -rf Telegram/ThirdParty/rlottie
%endif

%build
# Building WebRTC using cmake...
%if %{with webrtc}
pushd tg_owt
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%ifarch x86_64
%if %{with ipo} && %{without clang}
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION:BOOL=ON \
%endif
%endif
%if %{with clang}
    -DCMAKE_C_COMPILER=%{_bindir}/clang \
    -DCMAKE_CXX_COMPILER=%{_bindir}/clang++ \
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
    -DTG_OWT_PACKAGED_BUILD:BOOL=ON
%cmake_build
popd
%endif

# Building Telegram Desktop using cmake...
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%ifarch x86_64
%if %{with ipo} && %{without clang}
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION:BOOL=ON \
%endif
%endif
%if %{with rlottie}
    -DDESKTOP_APP_LOTTIE_USE_CACHE:BOOL=OFF \
%endif
%if %{with webrtc}
    -DDESKTOP_APP_DISABLE_WEBRTC_INTEGRATION:BOOL=OFF \
    -Dtg_owt_DIR:PATH=%{_builddir}/%{appname}-%{version}-full/tg_owt/%_vpath_builddir \
%else
    -DDESKTOP_APP_DISABLE_WEBRTC_INTEGRATION:BOOL=ON \
%endif
%if %{with clang}
    -DCMAKE_C_COMPILER=%{_bindir}/clang \
    -DCMAKE_CXX_COMPILER=%{_bindir}/clang++ \
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
    -DTDESKTOP_API_ID=611335 \
    -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
    -DDESKTOP_APP_USE_PACKAGED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=ON \
    -DDESKTOP_APP_USE_GLIBC_WRAPS:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
%if %{with gtk3}
    -DTDESKTOP_DISABLE_GTK_INTEGRATION:BOOL=OFF \
%else
    -DTDESKTOP_DISABLE_GTK_INTEGRATION:BOOL=ON \
%endif
    -DTDESKTOP_LAUNCHER_BASENAME=%{launcher}
%cmake_build

%install
%cmake_install

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{launcher}.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/%{launcher}.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{launcher}.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_metainfodir}/%{launcher}.appdata.xml

%changelog
* Wed Oct 07 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.4.3-1
- Updated to version 2.4.3.

* Fri Oct 02 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.4.2-1
- Updated to version 2.4.2.

* Fri Oct 02 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.4.1-1
- Updated to version 2.4.1.
