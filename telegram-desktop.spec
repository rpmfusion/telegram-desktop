%ifarch aarch64
    %global _lto_cflags %nil
%endif

# Telegram Desktop's constants...
%global appname tdesktop

# Reducing debuginfo verbosity...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

Name: telegram-desktop
Version: 6.4.2
Release: 2%{?dist}

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

Patch0: findprotobuf_fix.patch

# Telegram Desktop require more than 8 GB of RAM on linking stage.
# Disabling all low-memory architectures.
ExclusiveArch: x86_64 aarch64

BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(fmt)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tg_owt)
BuildRequires: cmake(tl-expected)
BuildRequires: cmake(ada)

BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(glibmm-2.68) >= 2.76.0
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(jemalloc)
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavfilter)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
%if 0%{?fedora} < 41
BuildRequires: pkgconfig(openssl)
%endif
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(protobuf-lite)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(webkitgtk-6.0)
BuildRequires: pkgconfig(xcb)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: pkgconfig(xcb-record)
BuildRequires: pkgconfig(xcb-screensaver)

BuildRequires: boost-devel
BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: ffmpeg-devel
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
BuildRequires: qt6-qtbase-static
BuildRequires: pkgconfig(openh264)
BuildRequires: cmake(KF6CoreAddons)
BuildRequires: cmake(tde2e)

Requires: hicolor-icon-theme
Requires: qt6-qtimageformats%{?_isa}
Requires: webkitgtk6.0%{?_isa}

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Virtual provides for bundled libraries...
Provides: bundled(cld3) = 3.0.13~gitb48dc46
Provides: bundled(kf5-kcoreaddons) = 5.106.0
Provides: bundled(libtgvoip) = 2.4.4~git7c46f4c
Provides: bundled(open-sans-fonts) = 1.10
Provides: bundled(plasma-wayland-protocols) = 1.6.0
Provides: bundled(rlottie) = 0~git8c69fc2
Provides: bundled(vazirmatn-fonts) = 27.2.2
Provides: bundled(cppgir) = 0~git69ef481c
Provides: bundled(minizip) = 1.2.13

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

# Unbundling libraries... except minizip
rm -rf Telegram/ThirdParty/{QR,dispatch,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,jemalloc,kimageformats,lz4,nimf,range-v3,xxHash}

# Fix minizip requrement
# sed -i 's|2.0.0|4.0.0|' cmake/external/minizip/CMakeLists.txt

%if 0%{?fedora} >= 41
sed -i "/#include <openssl\/engine.h>/d" Telegram/SourceFiles/core/utils.cpp
%endif

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
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
    -DDESKTOP_APP_DISABLE_QT_PLUGINS:BOOL=ON
%cmake_build

%install
%cmake_install

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/Telegram
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/dbus-1/services/org.telegram.desktop.service
%{_metainfodir}/*.metainfo.xml

%changelog
* Mon Feb 02 2026 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 6.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Mon Jan 12 2026 Vasiliy Glazov <vascom2@gmail.com> - 6.4.2-1

* Wed Dec 24 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.3.10-1
- Update to 6.3.10

* Tue Dec 16 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.3.9-1
- Update to 6.3.9

* Sat Dec 06 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.3.6-1
- Update to 6.3.6

* Thu Nov 27 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.3.4-1
- Update to 6.3.4

* Fri Nov 21 2025 Vasiliy Glazov <vascom2@gmail.com> 6.3.2-1
- Update to 6.3.2

* Mon Nov 17 2025 Vasiliy Glazov <vascom2@gmail.com> 6.3.1-1
- Update to 6.3.1

* Sat Nov 15 2025 Vasiliy Glazov <vascom2@gmail.com> 6.3.0-1
- Update to 6.3.0

* Thu Nov 06 2025 Leigh Scott <leigh123linux@gmail.com> - 6.2.4-3
- Rebuild for ffmpeg-8.0

* Mon Nov 03 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.2.4-2
- Rebuild for new Qt

* Thu Oct 23 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.2.4-1
- Update to 6.2.4

* Mon Oct 13 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.2.3-1
- Update to 6.2.3

* Tue Oct 07 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.1.4-1
- Update to 6.1.4

* Mon Sep 08 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.1.3-1
- Update to 6.1.3

* Thu Sep 04 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.1.2-1
- Update to 6.1.2

* Tue Sep 02 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.1.1-1
- Update to 6.1.1

* Mon Sep 01 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.1.0-1
- Update to 6.1.0

* Fri Aug 22 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.0.3-1
- Update to 6.0.3

* Tue Aug 05 2025 Vasiliy Glazov <vascom2@gmail.com> - 6.0.2-1
- Update to 6.0.2

* Sun Jul 27 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 5.14.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Sat May 10 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.14.2-1
- Update to 5.14.2

* Sat May 03 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.14.1-1
- Update to 5.14.1

* Wed Apr 09 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.13.1-2
- Rebuild for new Qt6

* Thu Mar 27 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.13.1-1
- Update to 5.13.1

* Fri Mar 21 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.12.6-1
- Update to 5.12.6

* Thu Mar 20 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.12.5-1
- Update to 5.12.5

* Mon Mar 10 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.12.3-1
- Update to 5.12.3

* Sun Feb 09 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.12.1-1
- Update to 5.12.1

* Fri Feb 14 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.11.1-1
- Update to 5.11.1

* Tue Jan 28 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.10.7-1
- Update to 5.10.7

* Mon Jan 27 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.10.6-1
- Update to 5.10.6

* Fri Jan 10 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.10.3-1
- Update to 5.10.3

* Thu Jan 09 2025 Vasiliy Glazov <vascom2@gmail.com> - 5.10.2-1
- Update to 5.10.2

* Thu Dec 19 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.9.1-1
- Update to 5.9.1

* Mon Dec 16 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.9.0-2
- Rebuild for new Qt6

* Wed Dec 04 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.9.0-1
- Update to 5.9.0

* Mon Nov 25 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.8.3-1
- Update to 5.8.3

* Tue Nov 19 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.8.2-1
- Update to 5.8.2

* Mon Nov 18 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.8.1-1
- Update to 5.8.1

* Sun Nov 17 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.8.0-1
- Update to 5.8.0

* Wed Nov 06 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.7.2-1
- Update to 5.7.2

* Tue Nov 05 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.7.1-1
- Update to 5.7.1
- Add patch for ffmpeg

* Mon Nov 04 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.6.3-2
- Rebuild for new Qt

* Thu Oct 17 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.6.3-1
- Update to 5.6.3

* Tue Oct 15 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.6.2-1
- Update to 5.6.2

* Tue Oct 08 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.6.1-1
- Update to 5.6.1

* Mon Oct 07 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.6.0-1
- Update to 5.6.0

* Thu Oct 03 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.5.5-1
- Update to 5.5.5

* Sat Aug 03 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.3.2-1
- Update to 5.3.2

* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 5.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Wed Jul 10 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.2.3-1
- Update to 5.2.3

* Wed Jul 03 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.2.2-1
- Update to 5.2.2

* Tue Jun 18 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.1.7-1
- Update to 5.1.7

* Wed May 29 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.0.4-1
- Update to 5.0.4

* Tue May 07 2024 Vasiliy Glazov <vascom2@gmail.com> - 5.0.1-1
- Update to 5.0.1

* Fri Apr 26 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.8-2
- Rebuild for new QT6

* Wed Apr 17 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.8-1
- Update to 4.16.8

* Tue Apr 16 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.7-1
- Update to 4.16.7

* Wed Apr 10 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.6-1
- Update to 4.16.6

* Tue Apr 09 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.5-1
- Update to 4.16.5

* Mon Apr 08 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.4-1
- Update to 4.16.4

* Sat Apr 06 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.3-1
- Update to 4.16.3

* Fri Apr 05 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.2-1
- Update to 4.16.2

* Wed Apr 03 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.16.1-1
- Update to 4.16.1

* Wed Mar 13 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.15.2-1
- Update to 4.15.2

* Sat Feb 24 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.15.0-3
- Rebuild

* Fri Feb 23 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.15.0-2
- Rebuild for new QT6

* Tue Feb 20 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.15.0-1
- Update to 4.15.0

* Sat Feb 10 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.15-1
- Update to 4.14.15

* Tue Feb 06 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.13-1
- Update to 4.14.13

* Fri Feb 02 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.12-1
- Update to 4.14.12

* Mon Jan 22 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.9-1
- Update to 4.14.9

* Tue Jan 09 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.4-1
- Update to 4.14.4

* Mon Jan 08 2024 Vasiliy Glazov <vascom2@gmail.com> - 4.14.3-1
- Update to 4.14.3

* Tue Dec 26 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.13.1-1
- Update to 4.13.1

* Mon Dec 04 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.12.2-1
- Update to 4.12.2

* Fri Dec 01 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.12.0-1
- Update to 4.12.0

* Mon Nov 13 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.7-1
- Update to 4.11.7

* Mon Nov 06 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.5-1
- Update to 4.11.5

* Sat Nov 04 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.3-2
- Rebuild

* Fri Nov 03 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.3-1
- Update to 4.11.3

* Thu Nov 02 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.2-1
- Update to 4.11.2

* Mon Oct 30 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.11.1-1
- Update to 4.11.1

* Tue Oct 24 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.10.3-3
- Rebuild with new Qt 6

* Tue Oct 10 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.10.3-2
- Rebuild with new Qt 6

* Tue Oct 03 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.10.3-1
- Update to 4.10.3

* Sun Oct 01 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.10.2-1
- Update to 4.10.2

* Mon Sep 25 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.10.1-1
- Update to 4.10.1

* Wed Sep 20 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.9-1
- Update to 4.9.9

* Sat Sep 16 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.8-1
- Update to 4.9.8

* Thu Sep 14 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.7-1
- Update to 4.9.7

* Wed Sep 06 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.5-1
- Update to 4.9.5

* Fri Sep 01 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.4-1
- Update to 4.9.4

* Wed Aug 23 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.9.3-1
- Update to 4.9.3

* Fri Aug 11 2023 Leigh Scott <leigh123linux@gmail.com> - 4.8.4-4
- Rebuild for new Qt

* Fri Jul 28 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.8.4-3
- Rebuild for new Qt 6

* Sun Jul 16 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.8.4-2
- Rebuilt due to Qt 6 private API export changes.

* Wed Jun 14 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.8.4-1
- Updated to version 4.8.4.

* Thu Jun 08 2023 Nicolas Chauvet <kwizart@gmail.com> - 4.8.1-4
- Rebuilt for qt6

* Wed May 31 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.8.1-3
- Fixed issues with voice and video calls.

* Sun May 07 2023 Vasiliy Glazov <vascom2@gmail.com> - 4.8.1-2
- Rebuild for new Qt 6

* Tue Apr 25 2023 Vitaly Zaitsev <vitaly@easycoding.org> - 4.8.1-1
- Updated to version 4.8.1.
