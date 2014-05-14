# TODO
# - integrate pld webapps framework
# - use pld %service
%define ver	1.05
%define subver	RC1
%include	/usr/lib/rpm/macros.perl
Summary:	Network monitoring program
Summary(pl.UTF-8):	Program do monitorowania sieci
Name:		demarc
Version:	%{ver}.%{subver}
Release:	4
License:	http://www.demarc.org/license/ (Free for non-commercial use)
Group:		Networking
Source0:	http://www.demarc.org/downloads/demarc-105/%{name}-%{ver}-%{subver}.tar.gz
# Source0-md5:	adf1550b8e7a4936c4b37ac214704f27
Source1:	%{name}-apache.conf
Source2:	%{name}.init
Source3:	%{name}.cron
Patch0:		%{name}-config.patch
Patch1:		%{name}-whois-fix.patch
URL:		http://www.demarc.org/
BuildRequires:	perl-Apache-DBI
BuildRequires:	perl-CGI
BuildRequires:	perl-DBI
BuildRequires:	perl-Digest-MD5
BuildRequires:	perl-Msql-Mysql-modules
BuildRequires:	perl-devel >= 1:5.6
BuildRequires:	rpm-perlprov >= 4.1-13
Requires(post,preun):	/sbin/chkconfig
Requires:	crondaemon
Requires:	rc-scripts
Requires:	webserver = apache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir		%{_sbindir}

%description
DEMARC is an all-inclusive network monitoring program that allows you
to monitor an entire network of servers from one powerful web
interface.

Instead of having one program perform file integrity checks, another
program monitoring the connectivity and health of your network, and
yet another monitoring your network for intrusion detection attempts,
DEMARC combines all three services into one powerful client/server
program. Not only can you monitor the status of the different machines
in your network, but you can also respond to changes in your network
all from one centralized location.

%description -l pl.UTF-8
DEMARC to kompletny system monitorowania sieci pozwalający monitorować
całą sieć serwerów z jednego interfejsu WWW.

Zamiast posiadać jeden program sprawdzający integralność plików, inny
program monitorujący połączenia i stan Twojej sieci, i jeszcze jeden
program monitorujący sieć w celach detekcji intruzów wystarczy DEMARC
łączący w sobie te trzy usługi w jednym programie klient/serwer. Nie
tylko możesz monitorować stan różnych maszyn w Twojej sieci ale także
możesz reagować na zmiany z jednej centralnej lokalizacji.

%package client
Summary:	Network monitoring program - client
Summary(pl.UTF-8):	Program do monitorowania sieci - klient
Group:		Networking
Requires:	snort(mysql) >= 1.8.1

%description client
DEMARC is an all-inclusive network monitoring program that allows you
to monitor an entire network of servers from one powerful web
interface.

This is client program which should be installed on all monitored
servers.

%description client -l pl.UTF-8
DEMARC to kompletny system monitorowania sieci pozwalający monitorować
całą sieć serwerów z jednego interfejsu WWW.

To jest program kliencki, który powinien być zainstalowany na
wszystkich monitorowanych serwerach.

%prep
%setup -q -n %{name}-%{ver}-%{subver}
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,cron.d,demarcd,httpd} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_datadir}/demarc/{images,cgi}} \
	$RPM_BUILD_ROOT%{_var}/lib/demarcd

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/demarcd
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/cron.d/%{name}
install -p bin/demarcd $RPM_BUILD_ROOT%{_sbindir}
cp -p conf/* $RPM_BUILD_ROOT%{_sysconfdir}/demarcd
cp -a cgi images $RPM_BUILD_ROOT%{_datadir}/demarc
cp -p install/{c*,d*,p*} $RPM_BUILD_ROOT%{_datadir}/demarc

%clean
rm -rf $RPM_BUILD_ROOT

%post
echo 'Remember to add "Include demarc.conf" to httpd.conf.'

%post client
if [ "$1" = "1" ] ; then
	touch /var/log/demarcd && chmod 750 /var/log/demarcd
fi
/sbin/chkconfig --add demarcd
if [ -f /var/lock/subsys/demarcd ]; then
	/etc/rc.d/init.d/demarcd restart 1>&2
else
	echo "Run \"%{_sbindir}/demarcd -I\" to install new snort sensor and then"
	echo "run \"/etc/rc.d/init.d/demarcd start\" to start demarcd daemon."
	echo "Note that in most cases there is no need to start \"snort\" as"
	echo "separate daemon, so turn it off using \"/sbin/chkconfig snort off\"."
fi


%preun client
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/demarcd ]; then
		/etc/rc.d/init.d/demarcd stop 1>&2
	fi
	/sbin/chkconfig --del demarcd
fi

%files
%defattr(644,root,root,755)
%doc install/{CHAN*,INS*,LIC*}
%dir %{_datadir}/demarc
%{_datadir}/demarc/create_mysql_demarc
%{_datadir}/demarc/db_patch_queries
%attr(755,root,root) %{_datadir}/demarc/*.pl

%dir %{_datadir}/demarc/cgi
%{_datadir}/demarc/cgi/StaticServices.pm
%attr(640,root,http) %{_datadir}/demarc/cgi/DEMARC_config.pm
%attr(755,root,root) %{_datadir}/demarc/cgi/demarc

%dir %{_datadir}/demarc/cgi/templates
%{_datadir}/demarc/cgi/templates/*

%dir %{_datadir}/demarc/images
%{_datadir}/demarc/images/*

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd/demarc.conf

%files client
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/demarcd
%attr(755,root,root) %{_sbindir}/demarcd
%attr(750,root,root) %dir %{_sysconfdir}/demarcd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/demarcd/*.conf
%attr(750,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/demarcd/*.cmds
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%attr(750,root,root) %{_var}/lib/demarcd
