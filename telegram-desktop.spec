%undefine __cmake_in_source_build
%global _lto_cflags %{nil}

# Build conditionals (with - OFF, without - ON)...
%bcond_with rlottie
%bcond_with gtk3
%bcond_with clang
%bcond_with libtgvoip

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

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
Version: 2.5.1
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPLv3+ with OpenSSL exception -- main tarball;
# * rlottie - LGPLv2+ -- static dependency;
# * qt_functions.cpp - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app
Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}-full.tar.gz

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

%if %{with libtgvoip}
BuildRequires: libtgvoip-devel >= 2.4.4
%else
Provides: bundled(libtgvoip) = 2.4.4
%endif

# Compilers and tools...
BuildRequires: desktop-file-utils
BuildRequires: libappstream-glib
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: gcc

# Development packages for Telegram Desktop...
BuildRequires: guidelines-support-library-devel >= 3.0.1
BuildRequires: qt5-qtbase-private-devel
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
BuildRequires: tg_owt-devel
BuildRequires: ninja-build
BuildRequires: glib2-devel
BuildRequires: opus-devel
BuildRequires: libatomic
BuildRequires: lz4-devel
BuildRequires: xz-devel
BuildRequires: python3

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

# Unbundling libraries...
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,libdbusmenu-qt,lz4,materialdecoration,minizip,nimf,qt5ct,range-v3,xxHash}

# Unbundling rlottie if build against packaged version...
%if %{with rlottie}
rm -rf Telegram/ThirdParty/rlottie
%endif

# Unbundling libtgvoip if build against packaged version...
%if %{with libtgvoip}
rm -rf Telegram/ThirdParty/libtgvoip
%endif

%build
# Building Telegram Desktop using cmake...
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%if %{with rlottie}
    -DDESKTOP_APP_LOTTIE_USE_CACHE:BOOL=OFF \
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
    -DDESKTOP_APP_DISABLE_WEBRTC_INTEGRATION:BOOL=OFF \
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
* Wed Dec 23 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.5.1-1
- Updated to version 2.5.1.

* Mon Nov 30 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.4.7-4
- Rebuilt due to Qt 5.15.2 update.

* Fri Nov 20 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.4.7-3
- Backported upstream patches with startup hangs fixes.
