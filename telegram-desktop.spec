# Enable or disable build with GTK support...
%bcond_without gtk3

# Enable or disable build using clang instead of gcc...
%bcond_with clang

# Telegram Desktop's constants...
%global appname tdesktop
%global apiid 208164
%global apihash dfbe1bc42dc9d20507e17d1814cc2f0a
%global upstreambase https://github.com/telegramdesktop

# Git revision of crl...
%global commit1 52baf11aaeb7f5ea6955a438abaa1aee4c4308d8
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Git revision of patched rlottie...
%global commit2 589db026ec211bc4979e3bffe074f6e48ce7cedc
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})

# Decrease debuginfo verbosity to reduce memory consumption...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

# Applying workaround to RHBZ#1559007...
%if %{with clang}
%global optflags %(echo %{optflags} | sed -e 's/-mcet//g' -e 's/-fcf-protection//g' -e 's/-fstack-clash-protection//g' -e 's/$/-Qunused-arguments -Wno-unknown-warning-option/')
%endif

Summary: Telegram Desktop official messaging app
Name: telegram-desktop
Version: 1.8.15
Release: 3%{?dist}

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
BuildRequires: range-v3-devel >= 0.9.1
BuildRequires: ffmpeg-devel >= 3.1
BuildRequires: openal-soft-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: libstdc++-devel
BuildRequires: openssl-devel
BuildRequires: xxhash-devel
BuildRequires: json11-devel
BuildRequires: opus-devel
BuildRequires: lz4-devel
BuildRequires: xz-devel
BuildRequires: python3

%if %{with gtk3}
BuildRequires: libappindicator-gtk3-devel
BuildRequires: glib2-devel
BuildRequires: gtk3-devel
Recommends: libappindicator-gtk3%{?_isa}
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
sed -i "$(($(wc -l < out/Release/CMakeLists.txt) - 2)) r Telegram/gyp/CMakeLists.inj" out/Release/CMakeLists.txt

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
mkdir -p %{buildroot}%{_bindir}
install -m 0755 -p out/Release/Telegram %{buildroot}%{_bindir}/%{name}

# Installing desktop shortcut...
mv lib/xdg/telegramdesktop.desktop lib/xdg/%{name}.desktop
desktop-file-install --dir=%{buildroot}%{_datadir}/applications lib/xdg/%{name}.desktop

# Installing icons...
for size in 16 32 48 64 128 256 512; do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    install -d $dir
    install -m 0644 -p Telegram/Resources/art/icon${size}.png $dir/%{name}.png
done

# Installing appdata for Gnome Software...
install -d %{buildroot}%{_metainfodir}
install -m 0644 -p lib/xdg/telegramdesktop.appdata.xml %{buildroot}%{_metainfodir}/%{name}.appdata.xml

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
* Tue Dec 24 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.15-3
- Removed GTK2 from build requirements.

* Tue Dec 17 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.15-2
- Fixed issue with menu bar on Gnome.
- Rebuilt due to Qt 5.13.2 update on Rawhide.

* Wed Oct 09 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 1.8.15-1
- Updated to version 1.8.15.
