Name:		   msat
Version:   1.0.9
Release:   1%{?dist}
Summary:   MSAT (Meta Spacewalk and Satellite). A collection of scripts for managing a Satellite or Spacewalk through the API.
Group:		 System/Scripts
License:	 GPLv3+
URL:		   http://msat.disruptivefoss.org/
Source0:	 %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-root
Requires:	 python

%description
MSAT (Meta SATellite) is about managing a Spacewalk or Satellite server in a scripted way. The python scripts connect to the Spacewalk or Satellite server and place the content of kickstart profiles, activation keys, and config channels and files on it.

%prep
%setup -q -n %{name}

%build
# Empty. Since no compilation or else is needed.

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/profile.d
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/msat

install api/msat.sh $RPM_BUILD_ROOT/etc/profile.d
install api/*.py $RPM_BUILD_ROOT/usr/local/bin/msat
install api/*.sh $RPM_BUILD_ROOT/usr/local/bin/msat
install api/sat.conf $RPM_BUILD_ROOT/usr/local/bin/msat

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Empty.

%preun
# Empty.

%files
%defattr(-,root,root,-)
%attr(0755,root,root) /etc/profile.d/msat.sh
%attr(0755,root,root) /usr/local/bin/msat

%changelog
* Mon Mar 30 2015 Gerben Welter <gerben.welter@prorail.nl> - 1.0.9-1
- Add module msat_mk_sc_repo to create repository.
* Thu Mar 26 2015 Gerben Welter <gerben.welter@prorail.nl> - 1.0.8-1
- Fix matching of rpms with an epoch.
* Fri Feb 20 2015 Gerben Welter <gerben.welter@prorail.nl> - 1.0.7-1
- Add new scripts.
* Mon Oct 13 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.6-1
- Fix removal of Configuration Channels in msat_rm_kp_hy.sh.
* Mon Oct 13 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.5-1
- Fix kickstart registration type
* Thu Oct 9 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.4-1
- Add msat_mk_er.py
- Change directory to better match other packages.
* Mon Sep 29 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.3-1
- Remove msat_wr_sc_rpms.py. Functionality is already provided
  by msat_wr_sc.py.
* Sun Sep 28 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.2-1
- Reinstate missing msat_wr_sc_rpms.py.
* Fri Sep 26 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.1-1
- Fix listing of RPMs with an epoch number.
* Mon Sep 22 2014 Gerben Welter <gerben.welter@prorail.nl> - 1.0.0-1
- Initial creation of package based on commit cc50e04.
