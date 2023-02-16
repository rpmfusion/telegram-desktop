# Build conditionals...
%global bundled_fonts 1
%global enable_wayland 1
%global enable_x11 1
%global legacy_ffmpeg 1
%global legacy_openssl 1

# Telegram Desktop's constants...
%global appname tdesktop

# Reducing debuginfo verbosity...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

# Workaround to GCC 13 lambda mangling conflict:
# RHBZ: https://bugzilla.redhat.com/show_bug.cgi?id=2168862
# GCC: https://gcc.gnu.org/PR107897
%if 0%{?fedora} && 0%{?fedora} >= 38
%global optflags %(echo %{optflags} -fabi-compat-version=0)
%endif

Name: telegram-desktop
Version: 4.6.3
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPL-3.0-or-later with OpenSSL exception -- main tarball;
# * tg_owt - BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND MIT AND LicenseRef-Fedora-Public-Domain -- static dependency;
# * rlottie - LGPL-2.1-or-later AND AND FTL AND BSD-3-Clause -- static dependency;
# * cld3  - Apache-2.0 -- static dependency;
# * qt_functions.cpp - LGPL-3.0-only -- build-time dependency;
# * open-sans-fonts  - Apache-2.0 -- bundled font;
# * vazirmatn-fonts - OFL-1.1 -- bundled font.
License: GPL-3.0-or-later AND BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND MIT AND LicenseRef-Fedora-Public-Domain AND LGPL-2.1-or-later AND FTL AND MPL-1.1 AND LGPL-3.0-only AND OFL-1.1
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app
Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}-full.tar.gz

# Telegram Desktop require more than 8 GB of RAM on linking stage.
# Disabling all low-memory architectures.
ExclusiveArch: x86_64 aarch64

BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tg_owt)
BuildRequires: cmake(tl-expected)

BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(glibmm-2.68)
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(jemalloc)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(protobuf-lite)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(vpx)

BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libappstream-glib
BuildRequires: libatomic
BuildRequires: libdispatch-devel
BuildRequires: libqrcodegencpp-devel
BuildRequires: libstdc++-devel
BuildRequires: minizip-compat-devel
BuildRequires: ninja-build
BuildRequires: python3
BuildRequires: qt6-qtbase-private-devel

%if %{bundled_fonts}
Provides: bundled(open-sans-fonts) = 1.10
Provides: bundled(vazirmatn-fonts) = 27.2.2
%else
Requires: open-sans-fonts
Requires: vazirmatn-fonts
%endif

%if %{enable_wayland}
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: qt6-qtbase-static
Provides: bundled(kf5-kcoreaddons) = 5.101.0
Provides: bundled(plasma-wayland-protocols) = 1.6.0
%endif

%if %{enable_x11}
BuildRequires: pkgconfig(xcb)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: pkgconfig(xcb-record)
BuildRequires: pkgconfig(xcb-screensaver)
%endif

%if 0%{?fedora} && 0%{?fedora} >= 37
BuildRequires: pkgconfig(webkit2gtk-4.1)
Requires: webkit2gtk4.1%{?_isa}
%else
BuildRequires: pkgconfig(webkit2gtk-4.0)
Requires: webkit2gtk3%{?_isa}
%endif

# Telegram Desktop has major issues when built against ffmpeg 5.x:
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=6273
# Upstream refuses to fix this issue:
# https://github.com/telegramdesktop/tdesktop/issues/24855
# https://github.com/telegramdesktop/tdesktop/issues/23899
%if %{legacy_ffmpeg}
BuildRequires: compat-ffmpeg4-devel
%else
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: ffmpeg-devel
Requires: ffmpeg-libs%{?_isa}
%endif

# Video calls doesn't work when built against openssl 3.0:
# https://github.com/telegramdesktop/tdesktop/issues/24698
%if %{legacy_openssl}
BuildRequires: openssl1.1-devel
Requires: openssl1.1%{?_isa}
%else
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(openssl)
%endif

%{?_qt6:Requires: %{_qt6}%{?_isa} = %{_qt6_version}}
Requires: hicolor-icon-theme
Requires: qt6-qtimageformats%{?_isa}

# Telegram Desktop can use native open/save dialogs with XDG portals.
Recommends: xdg-desktop-portal%{?_isa}
Recommends: (xdg-desktop-portal-gnome%{?_isa} if gnome-shell%{?_isa})
Recommends: (xdg-desktop-portal-kde%{?_isa} if plasma-workspace-wayland%{?_isa})
Recommends: (xdg-desktop-portal-wlr%{?_isa} if wlroots%{?_isa})

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Virtual provides for bundled libraries...
Provides: bundled(cld3) = 3.0.13~gitb48dc46
Provides: bundled(libtgvoip) = 2.4.4
Provides: bundled(rlottie) = 0~git8c69fc2

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
rm -rf Telegram/ThirdParty/{GSL,QR,dispatch,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,jemalloc,kimageformats,lz4,minizip,nimf,range-v3,xxHash}

%build
# Building Telegram Desktop using cmake...
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm \
    -DTDESKTOP_API_ID=611335 \
    -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
    -DDESKTOP_APP_USE_PACKAGED:BOOL=ON \
%if %{bundled_fonts}
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=OFF \
%else
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=ON \
%endif
%if %{enable_wayland}
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=ON \
%endif
%if %{enable_x11}
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=ON \
%endif
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON
%cmake_build

%install
%cmake_install

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_metainfodir}/*.metainfo.xml

%changelog
* Thu Feb 16 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.6.3-1
- Updated to version 4.6.3.

* Thu Feb 09 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.6.2-1
- Updated to version 4.6.2.

* Tue Feb 07 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.6.1-1
- Updated to version 4.6.1.

* Mon Feb 06 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.6.0-1
- Updated to version 4.6.0.

* Wed Feb 01 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.3-2
- Rebuilt due to Qt 6.4.2 update.

* Sat Jan 07 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.3-1
- Updated to version 4.5.3.

* Wed Jan 04 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.2-2
- Removed explicit dependency on compat-ffmpeg4.

* Tue Jan 03 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.2-1
- Updated to version 4.5.2.

* Mon Jan 02 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.1-1
- Updated to version 4.5.1.

* Sat Dec 31 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 4.5.0-1
- Updated to version 4.5.0.

* Thu Dec 08 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 4.4.1-1
- Updated to version 4.4.1.

* Sat Nov 26 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 4.3.4-1
- Updated to version 4.3.4.

* Tue Nov 08 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 4.3.1-1
- Updated to version 4.3.1.

* Sun Nov 06 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 4.3.0-1
- Updated to version 4.3.0.
