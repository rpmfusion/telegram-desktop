%undefine __cmake_in_source_build

# Build conditionals (with - OFF, without - ON)...
%bcond_with clang
%bcond_with libtgvoip
%bcond_with rlottie
%bcond_with wayland
%bcond_with webkit
%bcond_with qt5
%bcond_without x11

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# Applying toolchain configuration...
%if %{with clang}
%global toolchain clang
%endif

# Applying some workaround for non-x86 architectures...
%ifnarch x86_64
%define _lto_cflags %{nil}
%global _smp_build_ncpus 1
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

Name: telegram-desktop
Version: 3.2.4
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
ExclusiveArch: x86_64 aarch64

BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tg_owt) >= 0-13
BuildRequires: cmake(tl-expected)

BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(glibmm-2.4)
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(jemalloc)
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(rnnoise)

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

%if %{with clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
%endif

%if %{with qt5}
BuildRequires: cmake(Qt5Core)
BuildRequires: cmake(Qt5DBus)
BuildRequires: cmake(Qt5Gui)
BuildRequires: cmake(Qt5Network)
BuildRequires: cmake(Qt5Svg)
BuildRequires: cmake(Qt5Widgets)
BuildRequires: cmake(Qt5XkbCommonSupport)
BuildRequires: cmake(dbusmenu-qt5)
BuildRequires: qt5-qtbase-private-devel
%else
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: qt6-qtbase-private-devel
Provides: bundled(dbusmenu-qt6) = 0.9.3
%endif

%if %{with webkit}
BuildRequires: pkgconfig(webkit2gtk-4.0)
Requires: webkit2gtk3%{?_isa}
%endif

%if %{with libtgvoip}
BuildRequires: pkgconfig(tgvoip) >= 2.4.4
%else
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(libpulse)
Provides: bundled(libtgvoip) = 2.4.4
%endif

%if %{with rlottie}
BuildRequires: cmake(rlottie)
%else
Provides: bundled(rlottie) = 0~git
%endif

%if %{with wayland}
%if %{with qt5}
BuildRequires: cmake(Qt5Concurrent)
BuildRequires: cmake(Qt5WaylandClient)
BuildRequires: qt5-qtbase-static
%else
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: qt6-qtbase-static
%endif
BuildRequires: cmake(KF5Wayland)
BuildRequires: pkgconfig(wayland-client)
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

# Telegram Desktop can use native open/save dialogs with XDG portals.
Recommends: xdg-desktop-portal%{?_isa}

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Obsolete shared version of tg_owt...
Obsoletes: tg_owt < 0-8

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
rm -rf Telegram/ThirdParty/{Catch,GSL,QR,SPMediaKeyTap,expected,fcitx-qt5,fcitx5-qt,jemalloc,hime,hunspell,lz4,materialdecoration,minizip,nimf,qt5ct,range-v3,xxHash}

# Unbundling libdbusmenu-qt if build against Qt5...
%if %{with qt5}
rm -rf Telegram/ThirdParty/libdbusmenu-qt
%endif

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
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
%if %{with qt5}
    -DDESKTOP_APP_QT6:BOOL=OFF \
%else
    -DDESKTOP_APP_QT6:BOOL=ON \
%endif
%if %{with webkit}
    -DDESKTOP_APP_DISABLE_WEBKITGTK:BOOL=OFF \
%else
    -DDESKTOP_APP_DISABLE_WEBKITGTK:BOOL=ON \
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
* Mon Nov 15 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 3.2.4-1
- Updated to version 3.2.4.
- Switched to Qt 6 with an option to build against Qt 5.
- Removed no longer supported by upstream use-flags.
- Fixed FTBFS related to ffmpeg 4.5 update on Rawhide.
- Enabled aarch64 architecture with some limitations.

* Fri Nov 12 2021 Leigh Scott <leigh123linux@gmail.com> - 3.0.1-2
- Rebuilt for new ffmpeg snapshot

* Thu Sep 02 2021 Alexey Gorgurov <alexfails@fedoraproject.org> - 3.0.1-1
- Updated to version 3.0.1.

* Wed Jul 28 2021 Leigh Scott <leigh123linux@gmail.com> - 2.8.8-3
- Disable gtk integration

* Wed Jul 28 2021 Leigh Scott <leigh123linux@gmail.com> - 2.8.8-2
- Add Buildrequires webkitgtk4-devel and enable gtk integration

* Tue Jul 27 2021 Leigh Scott <leigh123linux@gmail.com> - 2.8.8-1
- Updated to version 2.8.8.

* Sun Mar 21 2021 Alexey Gorgurov <alexfails@fedoraproject.org> - 2.7.1-1
- Updated to version 2.7.1.

* Thu Feb 25 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.6.1-1
- Updated to version 2.6.1.

* Wed Feb 24 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.6.0-1
- Updated to version 2.6.0.

* Thu Feb 18 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 2.5.9-1
- Updated to version 2.5.9.
