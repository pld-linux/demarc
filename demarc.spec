%include	/usr/lib/rpm/macros.perl
%define ver	1.05
%define subver	RC1
Summary:	Network monitoring program
Summary(pl):	Program do monitorowania sieci
Name:		demarc
Version:	%{ver}.%{subver}
Release:	1
License:	http://www.demarc.org/license/
Group:		Networking
Group(de):	Netzwerkwesen
Group(es):	Red
Group(pl):	Sieciowe
Group(pt_BR):	Rede
Source0:	http://www.demarc.org/downloads/demarc-105/demarc-%{ver}-%{subver}.tar.gz
Source1:	%{name}-apache.conf
Source2:	%{name}.init
Source3:	%{name}.cron
Patch0:		%{name}-config.patch
URL:		http://www.demarc.org/
BuildRequires:	rpm-perlprov >= 4.0
BuildRequires:	perl >= 5.6
BuildRequires:	perl-CGI
BuildRequires:	perl-DBI
BuildRequires:	perl-Msql-Mysql-modules
BuildRequires:	perl-Digest-MD5
# BuildRequires:  perl(Apache::DBI)  (what package? FIXME)
Requires:	apache
Requires:	/etc/cron.d
Prereq:		rc-scripts
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

%description -l pl
DEMARC to kompletny system monitorowania sieci pozwalaj±cy monitorowaæ
ca³± sieæ serwerów z jednego interfejsu www.

Zamiast posiadaæ jeden program sprawdzaj±cy integralno¶c plików, inny
program monitoruj±cy po³±czenia i stan Twojej sieci, i jeszcze jeden
program monitoruj±cy sieæ w celach detekcji intruzów wystarczy DEMARC
³±cz±cy w sobie te trzy us³ugi w jednym programie klient/serwer. Nie
tylko mo¿esz monitorowaæ stan ró¿nych maszyn w Twojej sieci ale tak¿e
mo¿esz reagowaæ na zmiany z jednej centralnej lokalizacji.

%package client
Summary:        Network monitoring program - client
Summary(pl):    Program do monitorowania sieci - klient
Requires:	snort >= 1.8.1
Group:          Networking

%description client
DEMARC is an all-inclusive network monitoring program that allows you
to monitor an entire network of servers from one powerful web
interface.

This is client program which should be installed on all monitored servers.

%description -l pl client
DEMARC to kompletny system monitorowania sieci pozwalaj±cy monitorowaæ
ca³± sieæ serwerów z jednego interfejsu www.

To jest program kliencki, który powinien byæ zainstalowany na wszystkich
monitorowanych serwerach.

%prep
%setup -q -n %{name}-%{ver}-%{subver}
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,cron.d,demarcd,httpd}
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_datadir}/demarc/{images,cgi}
install -d $RPM_BUILD_ROOT/var/state/demarcd

install %{SOURCE1}		$RPM_BUILD_ROOT/etc/httpd/%{name}.conf
install %{SOURCE2}		$RPM_BUILD_ROOT/etc/rc.d/init.d/demarcd
install %{SOURCE3}		$RPM_BUILD_ROOT/etc/cron.d/%{name}
install bin/demarcd		$RPM_BUILD_ROOT%{_sbindir}
install conf/*			$RPM_BUILD_ROOT/etc/demarcd
cp -ar  cgi images		$RPM_BUILD_ROOT%{_datadir}/demarc
install install/{c*,d*,p*}	$RPM_BUILD_ROOT%{_datadir}/demarc

gzip -9nf install/{CHAN*,INS*,LIC*}

%clean
rm -rf $RPM_BUILD_ROOT

%post
echo 'Remember to add "Include demarc.conf" to httpd.conf and note that'
echo 'in most cases there is no need to start "snort" as separate'
echo 'daemon, so turn it off using "/sbin/chkconfig snort off".'

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
%doc install/*.gz
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

%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/httpd/demarc.conf

%files client
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/demarcd
%attr(755,root,root) %{_sbindir}/demarcd
%attr(750,root,root) %dir /etc/demarcd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/demarcd/*.conf
%attr(750,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/demarcd/*.cmds
%attr(640,root,root) %config /etc/cron.d/%{name}
%attr(750,root,root) /var/state/demarcd
