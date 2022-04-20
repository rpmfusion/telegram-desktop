%undefine __cmake_in_source_build

# Build conditionals...
%global enable_wayland 1
%global enable_x11 1
%global use_clang 0

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# Applying toolchain configuration...
%if %{use_clang}
%global toolchain clang
%endif

# Applying some workaround for non-x86 architectures...
%ifnarch x86_64
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

Name: telegram-desktop
Version: 3.7.1
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
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(webkit2gtk-4.0)

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

%if %{use_clang}
BuildRequires: compiler-rt
BuildRequires: clang
BuildRequires: llvm
%endif

%if %{enable_wayland}
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(wayland-protocols)
BuildRequires: qt6-qtbase-static
Provides: bundled(kf5-kwayland) = 5.93.0
Provides: bundled(plasma-wayland-protocols) = 1.6.0
%endif

%if %{enable_x11}
BuildRequires: pkgconfig(xcb)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: pkgconfig(xcb-record)
BuildRequires: pkgconfig(xcb-screensaver)
%endif

# Fedora now has a stripped ffmpeg. Make sure we're using the full version.
%if 0%{?fedora} && 0%{?fedora} >= 36
BuildRequires: ffmpeg-devel
Requires: ffmpeg-libs%{?_isa}
%endif

%{?_qt6:Requires: %{_qt6}%{?_isa} = %{_qt6_version}}
Requires: hicolor-icon-theme
Requires: open-sans-fonts
Requires: qt6-qtimageformats%{?_isa}
Requires: webkit2gtk3%{?_isa}

# Telegram Desktop can use native open/save dialogs with XDG portals.
Recommends: xdg-desktop-portal%{?_isa}
Recommends: (xdg-desktop-portal-gnome%{?_isa} if gnome-shell%{?_isa})
Recommends: (xdg-desktop-portal-kde%{?_isa} if plasma-workspace-wayland%{?_isa})
Recommends: (xdg-desktop-portal-wlr%{?_isa} if wlroots%{?_isa})

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Virtual provides for bundled libraries...
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
rm -rf Telegram/ThirdParty/{GSL,QR,dispatch,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,jemalloc,lz4,minizip,nimf,range-v3,xxHash}

%build
# Building Telegram Desktop using cmake...
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
%if %{use_clang}
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
    -DDESKTOP_APP_QT6:BOOL=ON \
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
    -DTDESKTOP_LAUNCHER_BASENAME=%{launcher}
%cmake_build

%install
%cmake_install

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{launcher}.metainfo.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/%{launcher}.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{launcher}.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_metainfodir}/%{launcher}.metainfo.xml

%changelog
* Wed Apr 20 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.7.1-1
- Updated to version 3.7.1.

* Mon Apr 18 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.7.0-1
- Updated to version 3.7.0.

* Thu Mar 17 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.6.1-1
- Updated to version 3.6.1.

* Fri Mar 11 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.6.0-1
- Updated to version 3.6.0.

* Wed Feb 16 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.5.2-2
- Rebuilt for Qt 6.2.3 update.

* Tue Feb 08 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.5.2-1
- Updated to version 3.5.2.

* Sat Feb 05 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.5.1-1
- Updated to version 3.5.1.

* Tue Feb 01 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.5.0-1
- Updated to version 3.5.0.

* Thu Jan 20 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.4.8-1
- Updated to version 3.4.8.

* Tue Jan 04 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.4.3-1
- Updated to version 3.4.3.

* Sat Jan 01 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 3.4.2-1
- Updated to version 3.4.2.
- Build against Qt 6 as recommended by the upstream.

* Thu Dec 30 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 3.4.0-1
- Updated to version 3.4.0.

* Thu Dec 09 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 3.3.0-1
- Updated to version 3.3.0.
- Enabled Wayland integration.
- Build with OpenSSL 3.0 for Fedora 36+.

* Tue Nov 16 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 3.2.5-1
- Updated to version 3.2.5.
- Added OpenSSL workaround for Fedora 36+.
- Adjusted the number of CPU cores on aarch64 during the build.
- Switched from boolean conditionals to constants.
- Build against Qt 5 due to issues with Qt 6 and Wayland.

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
