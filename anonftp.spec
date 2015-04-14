%define	name	anonftp
%define	version	3.0
%define rel	38
%define	release	%{rel}

Summary:	A program which enables anonymous FTP access
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
Source0:	recompress.c.bz2
AutoReqProv:	0
Requires(post):	wu-ftpd
Requires(preun): wu-ftpd
BuildRequires:	ash
BuildRequires:	termcap-devel
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
mkdir -p %{buildroot}%{_var}/ftp/{pub,etc,bin,lib}

cat > %{buildroot}%{_var}/ftp/etc/passwd <<EOF
root:*:0:0:::
bin:*:1:1:::
operator:*:11:0:::
ftp:*:14:50:::
nobody:*:99:99:::
EOF

cat > %{buildroot}%{_var}/ftp/etc/group <<EOF
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

%ifarch %{ix86} x86_64
LIBCSOVER=6
LIBNSLVER=1
%endif

%ifarch alpha
LIBCSOVER=6.1
LIBNSLVER=1.1
%endif


%define ROOT %{buildroot}%{_var}/ftp/lib

cp -fd /etc/ld.so.cache %{buildroot}%{_var}/ftp/etc
cp -fd /%{_lib}/libc.so.$LIBCSOVER /lib/libc-%{LIBCVER}.so %{ROOT}
cp -fd /lib/ld-linux.so.%{LDSOVER} /lib/ld-%{LIBCVER}.so %{ROOT}
cp -fd /%{_lib}/libnss_files-%{LIBCVER}.so \
	/%{_lib}/libnss_files.so.%{LIBNSSVER}	%{ROOT}
cp -fd /%{_lib}/libnsl-%{LIBCVER}.so /lib/libnsl.so.$LIBNSLVER %{ROOT}

cp -fd /%{_lib}/libnss_dns-%{LIBCVER}.so \
        /%{_lib}/libnss_dns.so.%{LIBNSSVER}       %{ROOT}
        
cp -fd /%{_lib}/libtermcap.so.2.0.8 %{ROOT}
cp -fd /%{_lib}/libtermcap.so.2 %{ROOT}

cp -fd /bin/ls /bin/cpio /bin/gzip /bin/tar %{buildroot}%{_var}/ftp/bin
cp -fd /bin/ash %{buildroot}%{_var}/ftp/bin/sh
ln -sf gzip %{buildroot}%{_var}/ftp/bin/zcat

install -m755 recompress -D %{buildroot}%{_var}/ftp/bin/recompress


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
%{_var}/ftp/lib/libc-%{LIBCVER}.so
%{_var}/ftp/lib/ld-linux.so.2
%{_var}/ftp/lib/ld-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_files-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_files.so.%{LIBNSSVER}
%{_var}/ftp/lib/libnss_dns-%{LIBCVER}.so
%{_var}/ftp/lib/libnss_dns.so.%{LIBNSSVER}
%{_var}/ftp/lib/libnsl-%{LIBCVER}.so
%{_var}/ftp/lib/libtermcap.so.2.0.8
%{_var}/ftp/lib/libtermcap.so.2
%endif
%attr(0755,root,root) %dir %{_var}/ftp
%attr(0111,root,root) %dir %{_var}/ftp/bin
%attr(0111,root,root) %dir %{_var}/ftp/etc
%attr(2755,root,ftp) %dir %{_var}/ftp/pub
%dir %{_var}/ftp/lib
%attr(0111,root,root) %{_var}/ftp/bin/ls
%attr(0111,root,root) %{_var}/ftp/bin/recompress
%attr(0111,root,root) %{_var}/ftp/bin/cpio
%attr(0111,root,root) %{_var}/ftp/bin/gzip
%attr(0111,root,root) %{_var}/ftp/bin/tar
%attr(0111,root,root) %{_var}/ftp/bin/zcat
%attr(0111,root,root) %{_var}/ftp/bin/sh


