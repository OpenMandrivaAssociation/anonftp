%define	name	anonftp
%define	version	3.0
%define rel	38
%define	release	%mkrel %{rel}

Summary:	A program which enables anonymous FTP access
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
Source0:	recompress.c.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
AutoReqProv:	0
Requires(post):	wu-ftpd
Requires(preun): wu-ftpd
BuildRequires:	ash
Requires:	ash
Requires:	setup >= 2.1.9-16mdk

%description
The anonftp package contains the files you need in order to
allow anonymous FTP access to your machine. Anonymous FTP access allows
anyone to download files from your machine without having a user account. 
Anonymous FTP is a popular way of making programs available via the
Internet.

You should install this if you are using wu-ftpd and wish to enable anonymous
downloads from your machine.

%prep
%setup -q -T -c %{name}-%{version}
bzcat %{SOURCE0} > recompress.c

%build
gcc $RPM_OPT_FLAGS -o recompress recompress.c

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_var}/ftp/{pub,etc,bin,lib}

cat > $RPM_BUILD_ROOT%{_var}/ftp/etc/passwd <<EOF
root:*:0:0:::
bin:*:1:1:::
operator:*:11:0:::
ftp:*:14:50:::
nobody:*:99:99:::
EOF

cat > $RPM_BUILD_ROOT%{_var}/ftp/etc/group <<EOF
root::0:
bin::1:
daemon::2:
sys::3:
adm::4:
ftp::50:
EOF

%define LDSOVER 2
%define LIBCVER %(rpm -q --qf '%%{version}' glibc)
%define LIBNSSVER 2
echo %LIBCVER

%ifarch %{ix86} sparc sparcv9 sparc64 armv4l ppc ia64 ppc64 x86_64
LIBCSOVER=6
LIBNSLVER=1
%endif

%ifarch alpha
LIBCSOVER=6.1
LIBNSLVER=1.1
%endif


%define ROOT $RPM_BUILD_ROOT%{_var}/ftp/lib

cp -fd /etc/ld.so.cache $RPM_BUILD_ROOT%{_var}/ftp/etc
cp -fd /%{_lib}/libc.so.$LIBCSOVER /lib/libc-%{LIBCVER}.so %{ROOT}

%ifarch ppc
cp -fd /%{_lib}/ld-%{LIBCVER}.so %{ROOT}
%else
cp -fd /lib/ld-linux.so.%{LDSOVER} /lib/ld-%{LIBCVER}.so %{ROOT}
%endif

cp -fd /%{_lib}/libnss_files-%{LIBCVER}.so \
	/%{_lib}/libnss_files.so.%{LIBNSSVER}	%{ROOT}
cp -fd /%{_lib}/libnsl-%{LIBCVER}.so /lib/libnsl.so.$LIBNSLVER %{ROOT}

cp -fd /%{_lib}/libnss_dns-%{LIBCVER}.so \
        /%{_lib}/libnss_dns.so.%{LIBNSSVER}       %{ROOT}

%ifnarch armv4l ppc
#cp -fd	/lib/libnss1_files-%{LIBCVER}.so %{ROOT}
cp -fd	/%{_lib}/libnss_files-%{LIBCVER}.so %{ROOT}
%endif

cp -fd /%{_lib}/libtermcap.so.2.0.8 %{ROOT}
cp -fd /%{_lib}/libtermcap.so.2 %{ROOT}

cp -fd /bin/ls /bin/cpio /bin/gzip /bin/tar $RPM_BUILD_ROOT%{_var}/ftp/bin
cp -fd /bin/ash $RPM_BUILD_ROOT%{_var}/ftp/bin/sh
ln -sf gzip $RPM_BUILD_ROOT%{_var}/ftp/bin/zcat
#cp -fd /usr/bin/compress $RPM_BUILD_ROOT%{_var}/ftp/bin

install -m755 recompress -D $RPM_BUILD_ROOT%{_var}/ftp/bin/recompress

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/ftpaccess ];then
		if ! grep -q "class.*anonymous.*"  /etc/ftpaccess;then
		cat /etc/ftpaccess | grep -v class > /etc/ftpaccess.mdk
		echo "class all real,guest,anonymous  *" > /etc/ftpaccess
		cat /etc/ftpaccess.mdk >> /etc/ftpaccess
		rm -f /etc/ftpaccess.mdk
		fi
fi
exit 0
%if %mdkversion < 200900
/sbin/ldconfig
%endif

%preun
if [ -f /etc/ftpaccess ];then
		grep -q class  /etc/ftpaccess && grep -v class /etc/ftpaccess > /etc/ftpaccess.mdk
		if [ "$?" = "0" ];then		
				mv -f /etc/ftpaccess.mdk /etc/ftpaccess
		fi
fi
exit 0


%files
%defattr(-,root,root)
%attr(0444,root,root) %config(noreplace) %{_var}/ftp/etc/passwd
%attr(0444,root,root) %config(noreplace) %{_var}/ftp/etc/group

%{_var}/ftp/etc/ld.so.cache

%ifarch alpha
%{_var}/ftp/lib/libc.so.6.1
%{_var}/ftp/lib/libnsl.so.1.1
%else
%{_var}/ftp/lib/libc.so.6
%{_var}/ftp/lib/libnsl.so.1

%endif
%{_var}/ftp/lib/libc-%{LIBCVER}.so
%ifnarch ppc
%{_var}/ftp/lib/ld-linux.so.%{LDSOVER}
%else
%{_var}/ftp/lib/ld.so.1
%endif
%{_var}/ftp/lib/ld-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_files-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_files.so.%{LIBNSSVER}
%{_var}/ftp/lib/libnss_dns-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_dns.so.%{LIBNSSVER}
%{_var}/ftp/lib/libnsl-%{LIBCVER}.so
%{_var}/ftp/lib/libtermcap.so.2.0.8
%{_var}/ftp/lib/libtermcap.so.2

%attr(0755,root,root) %dir %{_var}/ftp
%attr(0111,root,root) %dir %{_var}/ftp/bin
%attr(0111,root,root) %dir %{_var}/ftp/etc
%attr(2755,root,ftp) %dir %{_var}/ftp/pub
%dir %{_var}/ftp/lib
%attr(0111,root,root) %{_var}/ftp/bin/ls
#%attr(0111,root,root) %{_var}/ftp/bin/compress
%attr(0111,root,root) %{_var}/ftp/bin/recompress
%attr(0111,root,root) %{_var}/ftp/bin/cpio
%attr(0111,root,root) %{_var}/ftp/bin/gzip
#%attr(0111,root,root) /home/ftp/bin/sh
%attr(0111,root,root) %{_var}/ftp/bin/tar
%attr(0111,root,root) %{_var}/ftp/bin/zcat
%attr(0111,root,root) %{_var}/ftp/bin/sh



%changelog
* Thu Dec 09 2010 Oden Eriksson <oeriksson@mandriva.com> 3.0-38mdv2011.0
+ Revision: 616563
- the mass rebuild of 2010.0 packages

* Wed Sep 02 2009 Thierry Vignaud <tv@mandriva.org> 3.0-37mdv2010.0
+ Revision: 424828
- fix build (do not hardcode glibc version)
- rebuild
- rebuild

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 3.0-35mdv2009.0
+ Revision: 222758
- we now use glibc-2.8, not 2.4
- fix #%%define is forbidden
- kill re-definition of %%buildroot on Pixel's request
- import anonftp

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot


* Thu Jul 13 2006 Lenny Cartier <lenny@mandriva.com> 3.0-35mdv2007.0
- rebuild

* Sat Apr 29 2006 Emmanuel Blindauer <blindauer@mandriva.org> 3.0-34mdk
- Fix ppc build

* Mon Mar 06 2006 Nicolas L�cureuil <neoclust@mandriva.org> 3.0-33mdk
- Fix LIBCVER

* Thu Nov 03 2005 Nicolas L�cureuil <neoclust@mandriva.org> 3.0-32mdk
- Fix PreReq
- Fix LIBCVER

* Wed May 04 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 3.0-31mdk
- fix 64 bit build
- fix buildrequires
- fix summary-ended-with-dot

* Fri Jan 14 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 3.0-30mdk
- move to glibc 2.3.4

* Sun Dec 26 2004 Abel Cheung <deaddog@mandrake.org> 3.0-29mdk
- Readd "BuildRequires: ash"

* Fri Jul 30 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 3.0-28mdk
- add libnss_dns* library to have reverse dns mapping (from Jürgen holm)
- cleanups

* Tue Mar 02 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 3.0-27mdk
- move to glibc 2.3.3

* Sat Nov 15 2003 Olivier Thauvin <thauvin@aerov.jussieu.fr> 3.0-26mdk
- Franck Villaume <fvill@freesurf.fr>
  - move to glibc 2.3.2

* Sun Dec 29 2002 Olivier Thauvin <thauvin@aerov.jussieu.fr> 3.0-25mdk
- rebuild for rpm and glibc

* Thu May 09 2002 Geoffrey Lee <snailtalk@mandrakesoft.com> 3.0-24mdk
- Changed the description -- only needed for wu-ftpd (askwar).

* Thu May  9 2002 Stefan van der Eijk <stefan@eijk.nu> 3.0-23mdk
- BuildRequires (ncompress gone)
- no more /usr/bin/compress
- updated LIBCVER

* Fri Feb 22 2002 David BAUDENS <baudens@mandrakesoft.com> 3.0-22mdk
- BuildRequires: ash

* Mon Oct 08 2001 Stefan van der Eijk <stefan@eijk.nu> 3.0-21mdk
- BuildRequires: cpio

* Mon Sep 10 2001 Renaud Chaillat <rchaillat@mandrakesoft.com> 3.0-20mdk
- Use glibc 2.2.4

* Tue Jun 26 2001 Matthias Badaire <mbadaire@mandrakesoft.com> 3.0-19mdk
- add ia64 support

* Fri May 25 2001 Geoffrey Le <snailtalk@mandrakesoft.com> 3.0-18mdk
- Use glibc 2.2.3.

* Sat Mar 10 2001 Stefan van der Eijk <s.vandereijk@chello.nl> 3.0-17mdk
- updated LIBCVER

* Sat Jan 27 2001 Stefan van der Eijk <s.vandereijk@chello.nl> 3.0-16mdk
- updated LIBCVER

* Mon Dec  4 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 3.0-15mdk
- updated for glibc-2.2

* Thu Sep 21 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 3.0-14mdk
- changed ftpserver to wu-ftpd in requirements to avoid conflict 
  with proftpd

* Wed Sep  6 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 3.0-13mdk
- added requires on setup (for /etc/passwd), including release 
  number

* Wed Sep  6 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 3.0-12mdk
- BM /home/ftp => %%{_var}/ftp, needs update in /etc/passwd 
  (admin needs move its public files manually)
- noreplace for passwd and group

* Thu Aug 24 2000 Renaud Chaillat <rchaillat@pc-1229.mandrakesoft.com> 3.0-11mdk
- compressed source

* Thu Jun  8 2000 Frederic Lepied <flepied@mandrakesoft.com> 3.0-10mdk
- added prereq on ftpserver to let the %%post do its job
right.

* Mon May 29 2000 Adam Lebsack <adam@mandrakesoft.com> 3.0-9mdk
- change ppc LIBCSOVER and LIBNSLOVER to 6 and 1, respectively
- remove ld-linux.so from ppc

* Tue May 16 2000 Daouda LO <daouda@mandrakesoft.com> 3.0-8mdk
- who forget to put libtermcap* to %%files ?? 

* Mon May 15 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 3.0-7mdk
- Remove ldconfig (let me know where it's needed)
- Fix build on alpha.

* Sun May 14 2000 Jean-Michel Dault <jmdault@mandrakesoft.com> 3.0-6mdk
- Fixed Yet Another Problem in Post Scripts (FYAPIPS).

* Sat May 13 2000 Jean-Michel Dault <jmdault@mandrakesoft.com> 3.0-5mdk
- Fix another problem in post scripts. (%%preun)
- added ldconfig

* Fri May 12 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 3.0-4mdk
- Fix post scripts again.
- Add libtermcap.so.2 for ls :\

* Mon May 08 2000 Jean-Michel Dault <jmdault@mandrakesoft.com> 3.0-3mdk
- removed reference to $RPM_BUILD_ROOT in post scripts (DOH!)

* Sat Apr 22 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 3.0-2mdk
- %%preun not %%postun. 

* Fri Apr  7 2000 Jean-Michel Dault <jmdault@mandrakesoft.com> 3.0-1mdk
- merged with Rawhide:
  Add BuildPrereqs
  add recompress from BeroFTPD - it's useful for ftpconversions
  remove sh. Having a shell in the chroot ftp-structure is a security
  problem, not a feature. 
- our recompress is actually in the file, not redhat ;-)

* Thu Apr  6 2000 Jean-Michel Dault <jmdault@mandrakesoft.com> 2.8-9mdk
- fix group
- new libc

* Sun Mar 19 2000 John Buswell <johnb@mandrakesoft.com>
- Fixed support for PPC

* Mon Jan 17 2000 Chmouel Boudjnah <chmouel@mandrakesoft.com> 2.8-6mdk

- ||: when fail on strip.

* Fri Jan 07 2000 Yoann Vandoorselaere <yoann@mandrakesoft.com>
- Removed conflict with /etc/ftpaccess from wu-ftpd package :
  use %%post && %%postun to modify it and don't include this file 
  as one of ours to avoid this problem.

* Tue Jan 04 2000 John Buswell <johnb@mandrakesoft.com> 2.2-8mdk
- Added ppc arch
- fixed anonymous access

* Sun Oct 31 1999 Axalon Bloodstone <axalon@linux-mandrake.com>
- Add a k6 arch
- glibc version 2.1.2

* Tue May 11 1999 Bernhard Rosenkränzer <bero@mandrakesoft.com>
- Some fixes (libc.so.6, not 6.1)
- fix build with arch=i[456789]86

* Tue May 11 1999 Bernhard Rosenkränzer <bero@mandrakesoft.com>
- Mandrake adaptions

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 5)
- glibc version 2.1.1

* Tue Jan 12 1999 Cristian Gafton <gafton@redhat.com>
- add sparc

* Tue Jan 12 1999 Jeff Johnson <jbj@redhat.com>
- fix defattr typo (#784)
- newer libc

* Wed Jan 06 1999 Cristian Gafton <gafton@redhat.com>
- abuse the %%attr settings instead of massive chown
- avoid cp-av because it breaks on symlinks (the wonders of lchown/chown
- rebuild for glibc 2.1

* Thu Sep 10 1998 Cristian Gafton <gafton@redhat.com>
- newer libc

* Thu Apr 30 1998 Cristian Gafton <gafton@redhat.com>
- updated for the newer glibc libs

* Thu Nov 06 1997 Donnie Barnes <djb@redhat.com>
- Built with glibc for the first time
- moved BuildRoot to /var/tmp
- mega-reworking of the spec file

* Mon Mar 03 1997 Erik Troan <ewt@redhat.com>
- Requires ftpserver virtual package now (which wu-ftpd provides).

