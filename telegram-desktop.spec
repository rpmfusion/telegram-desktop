%undefine __cmake_in_source_build

# Build conditionals (with - OFF, without - ON)...
%bcond_with clang
%bcond_with gtk3
%bcond_with libtgvoip
%bcond_with rlottie
%bcond_with wayland
%bcond_without x11

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# Applying toolchain configuration...
%if %{with clang}
%global toolchain clang
%endif

Name: telegram-desktop
Version: 2.6.1
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

BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt5Core)
BuildRequires: cmake(Qt5DBus)
BuildRequires: cmake(Qt5Gui)
BuildRequires: cmake(Qt5Network)
BuildRequires: cmake(Qt5Widgets)
BuildRequires: cmake(Qt5XkbCommonSupport)
BuildRequires: cmake(dbusmenu-qt5)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tg_owt)
BuildRequires: cmake(tl-expected)

BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavresample)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(opus)

BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libappstream-glib
BuildRequires: libatomic
BuildRequires: libqrcodegencpp-devel
BuildRequires: libstdc++-devel
BuildRequires: minizip-compat-devel
BuildRequires: ninja-build
BuildRequires: python3
BuildRequires: qt5-qtbase-private-devel

%if %{with clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
%endif

%if %{with gtk3}
BuildRequires: pkgconfig(gtk+-3.0)
Requires: gtk3%{?_isa}
%endif

%if %{with libtgvoip}
BuildRequires: pkgconfig(tgvoip) >= 2.4.4
%else
Provides: bundled(libtgvoip) = 2.4.4
%endif

%if %{with rlottie}
BuildRequires: cmake(rlottie)
%else
Provides: bundled(rlottie) = 0~git
%endif

%if %{with wayland}
BuildRequires: cmake(KF5Wayland)
BuildRequires: cmake(Qt5WaylandClient)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: qt5-qtbase-static
%endif

%if %{with x11}
BuildRequires: pkgconfig(xcb)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: pkgconfig(xcb-record)
BuildRequires: pkgconfig(xcb-screensaver)
%endif

# Telegram Desktop require exact version of Qt due to Qt private API usage.
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
Requires: hicolor-icon-theme
Requires: open-sans-fonts
Requires: qt5-qtimageformats%{?_isa}

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

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
    -DDESKTOP_APP_DISABLE_GTK_INTEGRATION:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_GTK_INTEGRATION:BOOL=ON \
%endif
%if %{with wayland}
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=ON \
%endif
%if %{with x11}
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=ON \
%endif
%if %{with rlottie}
    -DDESKTOP_APP_LOTTIE_USE_CACHE:BOOL=OFF \
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
* Thu Feb 25 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.6.1-1
- Updated to version 2.6.1.

* Wed Feb 24 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.6.0-1
- Updated to version 2.6.0.

* Thu Feb 18 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.5.9-1
- Updated to version 2.5.9.
