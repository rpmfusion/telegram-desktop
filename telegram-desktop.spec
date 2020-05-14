# Build conditionals (with - OFF, without - ON)...
%bcond_without rlottie
%bcond_without ipo
%bcond_with clang

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/-Qunused-arguments -Wno-unknown-warning-option -Wno-deprecated-declarations/')
%endif

# Decrease debuginfo verbosity to reduce memory consumption...
%ifarch x86_64
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%else
%global optflags %(echo %{optflags} | sed 's/-g /-g2 /')
%endif

Name: telegram-desktop
Version: 2.1.6
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPLv3+ with OpenSSL exception -- main tarball;
# * rlottie - LGPLv2+ -- static dependency;
# * qt_functions.cpp - LGPLv3 -- build-time dependency.
License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app
ExclusiveArch: x86_64

# Source files...
Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}-full.tar.gz

# Telegram Desktop require exact version of Qt due to Qt private API usage.
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
Requires: qt5-qtimageformats%{?_isa}
Requires: hicolor-icon-theme
Requires: open-sans-fonts

# Short alias for the main package...
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
BuildRequires: mapbox-variant-devel >= 0.3.6
BuildRequires: qt5-qtbase-private-devel
BuildRequires: libtgvoip-devel >= 2.4.4
BuildRequires: range-v3-devel >= 0.10.0
BuildRequires: libqrcodegencpp-devel
BuildRequires: minizip-compat-devel
BuildRequires: ffmpeg-devel >= 3.1
BuildRequires: dbusmenu-qt5-devel
BuildRequires: openal-soft-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: libstdc++-devel
BuildRequires: expected-devel
BuildRequires: hunspell-devel
BuildRequires: openssl-devel
BuildRequires: xxhash-devel
BuildRequires: json11-devel
BuildRequires: ninja-build
BuildRequires: glib2-devel
BuildRequires: opus-devel
BuildRequires: lz4-devel
BuildRequires: xz-devel
BuildRequires: python3

%if %{with clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
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
mkdir -p %{_target_platform}

# Unbundling libraries...
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,libdbusmenu-qt,libqtxdg,libtgvoip,lxqt-qtplugin,lz4,materialdecoration,minizip,nimf,qt5ct,range-v3,variant,xxHash}

# Unbundling rlottie if build against packaged version...
%if %{with rlottie}
rm -rf Telegram/ThirdParty/rlottie
%endif

%build
# Building Telegram Desktop using cmake...
pushd %{_target_platform}
    %cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%ifarch x86_64
%if %{with ipo} && %{without clang}
    -DDESKTOP_APP_ENABLE_IPO_OPTIMIZATIONS:BOOL=ON \
%endif
%endif
%if %{with rlottie}
    -DDESKTOP_APP_USE_PACKAGED_RLOTTIE:BOOL=ON \
    -DDESKTOP_APP_LOTTIE_USE_CACHE:BOOL=OFF \
%else
    -DDESKTOP_APP_USE_PACKAGED_RLOTTIE:BOOL=OFF \
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
    -DDESKTOP_APP_USE_PACKAGED_GSL:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_EXPECTED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_VARIANT:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_QRCODE:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=ON \
    -DDESKTOP_APP_USE_GLIBC_WRAPS:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
    -DTDESKTOP_USE_PACKAGED_TGVOIP:BOOL=ON \
    -DTDESKTOP_DISABLE_GTK_INTEGRATION:BOOL=ON \
    -DTDESKTOP_DISABLE_REGISTER_CUSTOM_SCHEME:BOOL=ON \
    -DTDESKTOP_DISABLE_DESKTOP_FILE_GENERATION:BOOL=ON \
    -DTDESKTOP_USE_FONTCONFIG_FALLBACK:BOOL=OFF \
    -DTDESKTOP_LAUNCHER_BASENAME=%{launcher} \
    ..
popd
%ninja_build -C %{_target_platform}

%install
%ninja_install -C %{_target_platform}

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
* Thu May 14 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.1.6-1
- Updated to version 2.1.6.

* Wed May 13 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.1.5-1
- Updated to version 2.1.5.

* Sat May 09 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 2.1.4-1
- Updated to version 2.1.4.
