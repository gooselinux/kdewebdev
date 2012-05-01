
%define make_cvs 1

Name:    kdewebdev
Summary: Web development applications 
Epoch:   6
Version: 3.5.10
Release: 14%{?dist}

License: GPLv2
Url:     http://kdewebdev.org/ 
Group:   Applications/Editors
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: ftp://ftp.kde.org/pub/kde/stable/%{version}/src/%{name}-%{version}.tar.bz2
Source1: http://download.sourceforge.net/quanta/css.tar.bz2
Source2: http://download.sourceforge.net/quanta/html.tar.bz2
Source3: http://download.sourceforge.net/quanta/php_manual_en_20030401.tar.bz2
Source4: http://download.sourceforge.net/quanta/javascript.tar.bz2
Source5: hi48-app-kxsldbg.png
# extract from kdewebdev-3.5.10 tarball, avoid multilib issue
Source6: kommanderplugin.tar.gz

# javascript docrc fix
Patch0: javascript.patch

# add missing icons for kxsldbg
Patch1: kdewebdev-3.5.4-kxsldbg-icons.patch

# fix regression in autoconf
Patch2: arts-acinclude.patch

# fix crash in kimagemapeditor by using freehand polygon
Patch3: kdewebdev-3.5.10-fix-freehand-crash.patch

%if %{make_cvs}
BuildRequires: automake libtool
%endif
BuildRequires: desktop-file-utils
BuildRequires: kdelibs3-devel >= %{version}
BuildRequires: libxslt-devel libxml2-devel
BuildRequires: perl

Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires(hint): tidy

Provides: kdewebdev3 = %{version}-%{release}

Obsoletes: quanta < %{epoch}:%{version}-%{release}
Provides:  quanta = %{epoch}:%{version}-%{release}

%define kommander_ver 1.2.2
#Obsoletes: kommander < %{kommander_ver}-%{release}
Provides:  kommander = %{kommander_ver}-%{release}

%description
%{summary}, including:
* kfilereplace: batch search and replace tool
* kimagemapeditor: HTML image map editor
* klinkstatus: link checker
* kxsldbg: xslt Debugger
* quanta+: web development

%package devel
Group: Development/Libraries
Summary: Header files and documentation for %{name} 
Provides: kdewebdev3-devel = %{version}-%{release}
Requires: kdelibs3-devel
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: quanta-devel < %{epoch}:%{version}-%{release}
%description devel
%{summary}.

%package libs
Summary: %{name} runtime libraries
Group:   System Environment/Libraries
Requires: kdelibs3%{?_isa} >= %{version}
%description libs
%{summary}.


%prep
%setup -q -a 1 -a 2 -a 3 -a 4
%patch0 -p0 -b .javascript
%patch1 -p1 -b .kxsldbg-icons
%patch2 -p1 -b .autoconf
%patch3 -p1 -b .freehand-crash

install -m644 -p %{SOURCE5} kxsldbg/

%if %{make_cvs}
# hack/fix for newer automake
  sed -iautomake -e 's|automake\*1.10\*|automake\*1.1[0-5]\*|' admin/cvs.sh
  make -f admin/Makefile.common cvs
%endif


%build
unset QTDIR && . /etc/profile.d/qt.sh

%configure \
  --includedir=%{_includedir}/kde \
  --disable-rpath \
  --enable-new-ldflags \
  --disable-debug --disable-warnings \
  --disable-dependency-tracking --enable-final \

make %{?_smp_mflags}


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot}

# install docs
for i in css html javascript ; do
   pushd $i
   ./install.sh <<EOF
%{buildroot}%{_datadir}/apps/quanta/doc
EOF
   popd
   rm -rf $i
done
cp -a php php.docrc %{buildroot}%{_datadir}/apps/quanta/doc/

# make symlinks relative
pushd %{buildroot}%{_docdir}/HTML/en
for i in *; do
   if [ -d $i -a -L $i/common ]; then
      rm -f $i/common
      ln -nfs ../common $i
   fi
done
popd

# rpmdocs
for dir in k* quanta; do
  for file in AUTHORS ChangeLog README TODO ; do
    test -s  "$dir/$file" && install -p -m644 -D "$dir/$file" "rpmdocs/$dir/$file"
  done
done

# install kommanderplugin.tar.gz
install -p -m644 %{SOURCE6} %{buildroot}%{_datadir}/apps/kdevappwizard/kommanderplugin.tar.gz

%post
for f in crystalsvg hicolor locolor ; do
  touch --no-create %{_datadir}/icons/$f 2> /dev/null ||:
done

%postun
if [ $1 -eq 0 ] ; then
for f in crystalsvg hicolor locolor ; do
  touch --no-create %{_datadir}/icons/$f 2> /dev/null ||:
  gtk-update-icon-cache -q %{_datadir}/icons/$f 2> /dev/null ||:
done
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :
fi

%posttrans
for f in crystalsvg hicolor locolor ; do
  gtk-update-icon-cache -q %{_datadir}/icons/$f 2> /dev/null ||:
done
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%doc rpmdocs/*
%{_bindir}/*
%{_libdir}/kde3/*
%{_datadir}/applications/kde/*
%{_datadir}/applnk/.hidden/*
%{_datadir}/apps/*
%doc %{_datadir}/apps/quanta/doc
%{_datadir}/config.kcfg/*
%{_datadir}/icons/crystalsvg/*/*/*
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/icons/locolor/*/*/*
%{_datadir}/mimelnk/application/*
%{_datadir}/services/*
%{_datadir}/servicetypes/*
%{_docdir}/HTML/en/*

%files libs
%defattr(-,root,root,-)
%{_libdir}/lib*.so.*
%{_libdir}/lib*.la

%files devel
%defattr(-,root,root,-)
%{_libdir}/lib*.so
%{_includedir}/kde/*


%changelog
* Wed Mar 09 2011 Than Ngo <than@redhat.com> - 6:3.5.10-14
- apply patch to fix crash in kimagemapeditor by using freehand polygon

* Mon Jan 24 2011 Than Ngo <than@redhat.com> - 6:3.5.10-13
- Resolves: bz#591964, multilib issue

* Mon Jan 24 2011 Than Ngo <than@redhat.com> - 6:3.5.10-12
- Resolves: bz#591964, disable timestamp to avoid multilib issue

* Mon Jan 17 2011 Than Ngo <than@redhat.com> - 6:3.5.10-11
- Resolves: bz#591964
   fix changelog, update css, html and javascript tarballs

* Mon Jan 17 2011 Than Ngo <than@redhat.com> - 6:3.5.10-9
- repack for rhel6

* Fri Nov 05 2010 Thomas Janssen <thomasj@fedoraproject.org> 6:3.5.10-8
- rebuild for new libxml2

* Tue Feb 02 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:3.5.10-7
- ressurrect -libs subpkg (legacy crud removal fallout)

* Mon Feb 01 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:3.5.10-6
- drop some legacy crud
- optimize scriptlets

* Fri Jan 22 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.10-5
- fix FTBFS with autoconf >= 2.64 (#538907)

* Wed Jul 29 2009 Rex Dieter <rdieter@fedoraproject.org> - 6:3.5.10-4
- FTBFS kdewebdev-3.5.10-2.fc11 (#511439)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.5.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:3.5.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Aug 30 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.10-1
- update to 3.5.10

* Wed Jun 04 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.9-4
- reinclude crystalsvg icons also on f9+ (no longer using crystalsvg from KDE 4)

* Fri Mar 28 2008 Rex Dieter <rdieter@fedoraproject.org> - 6:3.5.9-3
- drop Requires: gnupg
- omit multilib upgrade hacks

* Tue Mar 04 2008 Rex Dieter <rdieter@fedoraproject.org> - 6:3.5.9-2
- -libs: Requires: %%name, fixes "yum update removes kdewebdev" (#435956)

* Fri Feb 15 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.9-1
- update to 3.5.9
- drop rename-arrow patch (fixed upstream, arrow icon is now app-local)
- drop gcc43 patch (fixed upstream)

* Sat Feb 09 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.8-7
- rebuild for GCC 4.3

* Sat Jan 05 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.8-6
- apply upstream build fix for GCC 4.3 (IS_BLANK macro name conflict w/ libxml)

* Mon Dec 24 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:3.5.8-5
- remove crystalsvg icon which conflicts with kdeartwork (F9+) (#426694)

* Wed Dec 5 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 6:3.5.8-4
- rename arrow.png because it confuses KDE 4 (kde#153476)
- drop BR: kdesdk3 on F9+

* Tue Oct 25 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 6:3.5.8-3
- -libs: Obsoletes: %%name ... to help out multilib upgrades
- -libs conditional (f8+)

* Mon Oct 15 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 6:3.5.8-2
- -libs subpkg (more multilib friendly
- kommander_ver 1.2.2

* Sat Oct 13 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 6:3.5.8-1
- kde-3.5.8

* Thu Sep 13 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 6:3.5.7-2
- License: GPLv2
- update %%description
- Provides: kdewebdev3 kommander 
- BR: kdelibs3

* Mon Jun 11 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 6:3.5.7-1
- 3.5.7
- +Requires(hint): gnupg tidy
- use Versioned Obsoletes/Provides: quanta

* Thu Feb 08 2007 Than Ngo <than@redhat.com> 6:3.5.6-1.fc7
- 3.5.6

* Fri Aug 25 2006 Than Ngo <than@redhat.com> 6:3.5.4-2
- fix #203893, add missing icon for kxsldbg

* Thu Aug 10 2006 Than Ngo <than@redhat.com> 6:3.5.4-1
- rebuild

* Mon Jul 24 2006 Than Ngo <than@redhat.com> 6:3.5.4-0.pre1
- prerelease of 3.5.4 (from the first-cut tag)

* Fri Jul 14 2006 Than Ngo <than@redhat.com> 6:3.5.3-2
- BR: autoconf automake libtool

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 6:3.5.3-1.1
- rebuild

* Mon Jun 05 2006 Than Ngo <than@redhat.com> 6:3.5.3-1
- update to 3.5.3

* Wed Apr 05 2006 Than Ngo <than@redhat.com> 6:3.5.2-1
- update to 3.5.2

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 6:3.5.1-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 6:3.5.1-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sun Feb 05 2006 Than Ngo <than@redhat.com> 6:3.5.1-1 
- 3.5.1

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sun Dec 04 2005 Than Ngo <than@redhat.com> 6:3.5.0-1
- 3.5

* Tue Oct 25 2005 Than Ngo <than@redhat.com> 6:3.4.92-1
- update to 3.5 beta2

* Mon Oct 10 2005 Than Ngo <than@redhat.com> 6:3.4.91-1
- update to 3.5 beta 1

* Mon Sep 26 2005 Than Ngo <than@redhat.com> 6:3.4.2-3
- remove tidy since it's included in extras #169217

* Thu Sep 22 2005 Than Ngo <than@redhat.com> 6:3.4.2-2
- fix uic build problem

* Thu Aug 11 2005 Than Ngo <than@redhat.com> 6:3.4.2-1
- update to 3.4.2

* Wed Jun 29 2005 Than Ngo <than@redhat.com> 6:3.4.1-1
- 3.4.1
- fix gcc4 build problem

* Wed May 04 2005 Than Ngo <than@redhat.com> 6:3.4.0-3
- apply patch to fix CAN-2005-0754, Kommander untrusted code execution,
  thanks to KDE security team

* Tue Apr 19 2005 Than Ngo <than@redhat.com> 6:3.4.0-2
- add kdesdk in buildrequires #155054

* Sat Mar 19 2005 Than Ngo <than@redhat.com> 6:3.4.0-1
- 3.4.0

* Fri Mar 04 2005 Than Ngo <than@redhat.com> 6:3.4.0-0.rc1.2
- rebuilt against gcc-4.0.0-0.31

* Mon Feb 28 2005 Than Ngo <than@redhat.com> 6:3.4.0-0.rc1.1
- 3.4.0 rc1

* Mon Feb 21 2005 Than Ngo <than@redhat.com> 6:3.3.92-0.1
- 3.4 beta2

* Fri Dec 03 2004 Than Ngo <than@redhat.com> 6:3.3.2-0.1
- update to 3.3.2
- add missing tidy for HTML syntax checking #140970

* Mon Oct 18 2004 Than Ngo <than@redhat.com> 6:3.3.1-2
- rebuilt

* Wed Oct 13 2004 Than Ngo <than@redhat.com> 6:3.3.1-1
- update to 3.3.1

* Thu Sep 16 2004 Than Ngo <than@redhat.com> 3.3.0-1
- update to 3.3.0

* Sat Jun 19 2004 Than Ngo <than@redhat.com> 3.2.3-1 
- update to 3.2.3

* Sun Apr 11 2004 Than Ngo <than@redhat.com> 3.2.2-0.1
- 3.2.2 release

* Fri Mar 05 2004 Than Ngo <than@redhat.com> 6:3.2.1-1
- 3.2.1 release

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 17 2004 Than Ngo <than@redhat.com> 6:3.2.0-1.2
- fix typo bug, _smp_mflags instead smp_mflags

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 11 2004 Than Ngo <than@redhat.com> 6:3.2.0-0.1
- 3.2.0 release
- built against qt 3.3.0

* Thu Jan 22 2004 Than Ngo <than@redhat.com> 6:3.1.95-0.1
- 3.2 RC1

* Thu Dec 11 2003 Than Ngo <than@redhat.com> 6:3.1.94-0.3
- fix build problem with new gcc

* Thu Dec 04 2003 Than Ngo <than@redhat.com> 6:3.1.94-0.2
- remove quanta-3.1.93-xml2.patch, which is included in upstream

* Mon Dec 01 2003 Than Ngo <than@redhat.com> 6:3.1.94-0.1
- KDE 3.2 Beta2

* Thu Nov 27 2003 Than Ngo <than@redhat.com> 6:3.1.93-0.3
- get rid of rpath

* Tue Nov 25 2003 Than Ngo <than@redhat.com> 6:3.1.93-0.2
- add fix to build against new libxml2 >= 2.6

* Thu Nov 13 2003 Than Ngo <than@redhat.com> 6:3.1.93-0.1
- KDE 3.2 Beta 1
- cleanup
- add devel package

* Tue Sep 30 2003 Than Ngo <than@redhat.com> 6:3.1.4-1
- 3.1.4

* Tue Aug 12 2003 Than Ngo <than@redhat.com> 6:3.1.3-1
- 3.1.3
- update php docs (bug #99073)
- desktop issue (bug #87602)


* Wed Jun 25 2003 Than Ngo <than@redhat.com> 3.1.2-4
- rebuilt

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 20 2003 Than Ngo <than@redhat.com> 3.1.2-2
- 3.1.2

* Thu Mar 20 2003 Than Ngo <than@redhat.com> 3.1.1-1
- 3.1.1

* Fri Jan 31 2003 Than Ngo <than@redhat.com> 3.1-1
- 3.1 final

* Sat Nov 30 2002 Than Ngo <than@redhat.com> 3.1-0.2
- cleanup scpecfile
- desktop file issue
- add missing %%post, %%postun ldconfig
- remove po files, it's now in kde-i18n stuff

* Thu Nov 28 2002 Than Ngo <than@redhat.com> 3.1-0.1
- update to 3.1 rc4

* Fri Aug 23 2002 Phil Knirsch <pknirsch@redhat.com> 3.0-0.pr1.5
- Rebuilt with new qt.

* Mon Aug 12 2002 Tim Powers <timp@redhat.com> 3.0-0.pr1.4
- rebuilt with gcc-3.2

* Sun Aug  4 2002 han Ngo <than@redhat.com> 3.0-0.pr1.3
- 3.0-pr1 release
- fixed desktop file issue

* Tue Jul 23 2002 Tim Powers <timp@redhat.com> 3.0-0.pr1.2
- build using gcc-3.2-0.1

* Sun Jul 14 2002 Than Ngo <than@redhat.com> 3.0-0.pr1.1
- 3.0-pr1 fixed bug #68268
- use desktop-file-install

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.1-0.cvs20020523.1
- Update, fix build with current toolchain

* Tue Apr 16 2002 Than Ngo <than@redhat.com> 2.1-0.cvs20020404.2
- rebuild

* Thu Apr  4 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.1-0.cvs20020404.1
- Fix bug #62648

* Tue Mar 26 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.1-0.cvs20020326.1
- Update
- %%langify spec file
- Move desktop file to /etc/X11/applnk; quanta is generally useful

* Tue Jan 29 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.1-0.cvs20020129.1
- Update, fix build, KDE3ify

* Thu Aug 23 2001 Than Ngo <than@redhat.com> 2.0-0.cvs20010724.2
- fix quanta crashes on exit (Bug #51180)
- fix bad character (Bug #51509)

* Tue Jul 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.0-0.cvs20010724.1
- langify
- remove ia64 workarounds
- update

* Mon Jul 23 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.0-0.cvs20010723.1
- Update
- Make symlinks relative

* Thu Feb 22 2001 Than Ngo <than@redhat.com>
- update to 2.0pr1

* Wed Feb  7 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Update to get rid of libkdefakes.so.0 requirement

* Thu Jan  4 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Initial build, obsoletes WebMaker
