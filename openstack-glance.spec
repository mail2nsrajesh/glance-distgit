%global release_name juno

Name:             openstack-glance
Version:          XXX
Release:          XXX{?dist}
Summary:          OpenStack Image Service

Group:            Applications/System
License:          ASL 2.0
URL:              http://glance.openstack.org
Source0:          https://launchpad.net/glance/%{release_name}/%{version}/+download/glance-%{version}.tar.gz

Source1:          openstack-glance-api.service
Source2:          openstack-glance-registry.service
Source3:          openstack-glance-scrubber.service
Source4:          openstack-glance.logrotate

Source5:          glance-api-dist.conf
Source6:          glance-registry-dist.conf
Source7:          glance-cache-dist.conf
Source8:          glance-scrubber-dist.conf

BuildArch:        noarch
BuildRequires:    python2-devel
BuildRequires:    python-setuptools
BuildRequires:    intltool

Requires(pre):    shadow-utils
Requires:         python-glance = %{version}-%{release}
Requires:         python-glanceclient >= 1:0
Requires:         openstack-utils
BuildRequires:    python-oslo-sphinx

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd

%description
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains the API and registry servers.

%package          common
Summary:          Components common to all OpenStack Glance services

%description      common
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains shared scripts configuration between all OpenStack glance
services.


%package          api
Summary:          OpenStack Glance API service
Requires:         openstack-glance-common = %{version}-%{release}

%description      api
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains the API and local cache servers.


%package          registry
Summary:          OpenStack Glance registry service
Requires:         openstack-glance-common = %{version}-%{release}

%description      registry
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains the registry server.


%package -n       python-glance
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         MySQL-python
Requires:         pysendfile
Requires:         python-eventlet
Requires:         python-httplib2
Requires:         python-iso8601
Requires:         python-jsonschema
Requires:         python-migrate >= 0.9.1
Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-sqlalchemy >= 0.8.4
Requires:         python-webob
Requires:         python-crypto
Requires:         pyxattr
Requires:         python-cinderclient
Requires:         python-glance-store
Requires:         python-keystoneclient >= 1:0.9.0
Requires:         python-keystonemiddleware
Requires:         python-swiftclient
Requires:         python-oslo-config >= 1:1.2.1
Requires:         python-oslo-messaging >= 1.4.0.0
Requires:         python-oslo-vmware
Requires:         python-oslo-i18n
Requires:         python-oslo-db
Requires:         python-osprofiler
Requires:         python-retrying
Requires:         python-six >= 1.7.0
Requires:         python-posix_ipc
Requires:         python-stevedore
Requires:         python-anyjson
Requires:         python-netaddr
Requires:         python-wsme >= 0.6
Requires:         pyOpenSSL
Requires:         python-pbr
Requires:         python-semantic-version
Requires:         python-elasticsearch

#test deps: python-mox python-nose python-requests
#test and optional store:
#ceph - glance.store.rdb
#python-boto - glance.store.s3
Requires:         python-boto

%description -n   python-glance
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains the glance Python library.

%package doc
Summary:          Documentation for OpenStack Image Service
Group:            Documentation

Requires:         %{name} = %{version}-%{release}

BuildRequires:    systemd-units
BuildRequires:    python-sphinx
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-eventlet
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob

%description      doc
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains documentation files for glance.

%prep
%setup -q -n glance-%{upstream_version}

sed -i '/\/usr\/bin\/env python/d' glance/common/config.py glance/common/crypt.py glance/db/sqlalchemy/migrate_repo/manage.py

# Remove the requirements file so that pbr hooks don't add it
# to distutils requiers_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

# Programmatically update defaults in example config
api_dist=%{SOURCE5}
registry_dist=%{SOURCE6}
cache_dist=%{SOURCE7}
scrubber_dist=%{SOURCE8}
for svc in api registry cache scrubber; do
  #  First we ensure all values are commented in appropriate format.
  #  Since icehouse, there was an uncommented keystone_authtoken section
  #  at the end of the file which mimics but also conflicted with our
  #  distro editing that had been done for many releases.
  sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' etc/glance-$svc.conf

  #  TODO: Make this more robust
  #  Note it only edits the first occurance, so assumes a section ordering in sample
  #  and also doesn't support multi-valued variables like dhcpbridge_flagfile.
  eval dist_conf=\$${svc}_dist
  while read name eq value; do
    test "$name" && test "$value" || continue
    sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/glance-$svc.conf
  done < $dist_conf
done

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python2_sitelib}/glance/tests

# Drop old glance CLI it has been deprecated
# and replaced glanceclient
rm -f %{buildroot}%{_bindir}/glance

export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-build -b html source build/html
sphinx-build -b man source build/man

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
rm -f %{buildroot}%{_sysconfdir}/glance*.conf
rm -f %{buildroot}%{_sysconfdir}/glance*.ini
rm -f %{buildroot}%{_sysconfdir}/logging.cnf.sample
rm -f %{buildroot}%{_sysconfdir}/policy.json
rm -f %{buildroot}%{_sysconfdir}/schema-image.json
rm -f %{buildroot}/usr/share/doc/glance/README.rst

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/glance
install -d -m 755 %{buildroot}%{_sharedstatedir}/glance/images

# Config file
install -p -D -m 640 etc/glance-api.conf %{buildroot}%{_sysconfdir}/glance/glance-api.conf
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_datadir}/glance/glance-api-dist.conf
install -p -D -m 644 etc/glance-api-paste.ini %{buildroot}%{_datadir}/glance/glance-api-dist-paste.ini
install -p -D -m 640 etc/glance-registry.conf %{buildroot}%{_sysconfdir}/glance/glance-registry.conf
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_datadir}/glance/glance-registry-dist.conf
install -p -D -m 644 etc/glance-registry-paste.ini %{buildroot}%{_datadir}/glance/glance-registry-dist-paste.ini
install -p -D -m 640 etc/glance-cache.conf %{buildroot}%{_sysconfdir}/glance/glance-cache.conf
install -p -D -m 644 %{SOURCE7} %{buildroot}%{_datadir}/glance/glance-cache-dist.conf
install -p -D -m 640 etc/glance-scrubber.conf %{buildroot}%{_sysconfdir}/glance/glance-scrubber.conf
install -p -D -m 644 %{SOURCE8} %{buildroot}%{_datadir}/glance/glance-scrubber-dist.conf

install -p -D -m 640 etc/policy.json %{buildroot}%{_sysconfdir}/glance/policy.json
install -p -D -m 640 etc/schema-image.json %{buildroot}%{_sysconfdir}/glance/schema-image.json

# systemd services
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/openstack-glance-api.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-glance-registry.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-glance-scrubber.service

# Logrotate config
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-glance

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/glance

# Install log directory
install -d -m 755 %{buildroot}%{_localstatedir}/log/glance

# Programmatically update defaults in sample config
# which is installed at /etc/$project/$program.conf
# TODO: Make this more robust
# Note it only edits the first occurance, so assumes a section ordering in sample
# and also doesn't support multi-valued variables.
for svc in api registry cache scrubber; do
  cfg=%{buildroot}%{_sysconfdir}/glance/glance-$svc.conf
  test -e $cfg || continue
  while read name eq value; do
    test "$name" && test "$value" || continue
    # Note some values in upstream glance config may not be commented
    # and if not, they might not match the default value in code.
    # So we comment out both froms to have dist config take precedence.
    sed -i "0,/^#* *$name *=/{s!^#* *$name *=.*!#$name=$value!}" $cfg
  done < %{buildroot}%{_datadir}/glance/glance-$svc-dist.conf
done

%pre common
getent group glance >/dev/null || groupadd -r glance -g 161
getent passwd glance >/dev/null || \
useradd -u 161 -r -g glance -d %{_sharedstatedir}/glance -s /sbin/nologin \
-c "OpenStack Glance Daemons" glance
exit 0

%post api
%systemd_post openstack-glance-api.service
%systemd_post openstack-glance-scrubber.service

%post registry
%systemd_post openstack-glance-registry.service


%preun api
%systemd_preun openstack-glance-api.service
%systemd_preun openstack-glance-scrubber.service

%preun registry
%systemd_preun openstack-glance-registry.service

%postun api
%systemd_postun_with_restart openstack-glance-api.service
%systemd_postun_with_restart openstack-glance-scrubber.service

%postun registry
%systemd_postun_with_restart openstack-glance-registry.service


%files
%doc README.rst
%license LICENSE
%{_bindir}/glance-control
%{_bindir}/glance-manage

%{_mandir}/man1/glance-control.1.*
%{_mandir}/man1/glance-manage.1.*


%files common
%license LICENSE
%dir %{_sysconfdir}/glance
%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/schema-image.json
%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/logrotate.d/openstack-glance
%dir %attr(0755, glance, nobody) %{_sharedstatedir}/glance
%dir %attr(0750, glance, glance) %{_localstatedir}/log/glance


%files api
%{_bindir}/glance-api
%{_bindir}/glance-cache-cleaner
%{_bindir}/glance-cache-manage
%{_bindir}/glance-cache-prefetcher
%{_bindir}/glance-cache-pruner
%{_bindir}/glance-index
%{_bindir}/glance-scrubber
%{_bindir}/glance-search

%{_mandir}/man1/glance-api.1.*
%{_mandir}/man1/glance-cache-*.1.*
%{_mandir}/man1/glance-scrubber.1.*

%{_datadir}/glance/glance-api-dist.conf
%{_datadir}/glance/glance-api-dist-paste.ini
%{_datadir}/glance/glance-cache-dist.conf
%{_datadir}/glance/glance-scrubber-dist.conf

%{_unitdir}/openstack-glance-api.service
%{_unitdir}/openstack-glance-scrubber.service

%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/policy.json
%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/glance-api.conf
%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/glance-cache.conf
%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/glance-scrubber.conf


%files registry
%{_bindir}/glance-registry
%{_bindir}/glance-replicator

%{_mandir}/man1/glance-registry.1.*
%{_mandir}/man1/glance-replicator.1.*

%{_datadir}/glance/glance-registry-dist.conf
%{_datadir}/glance/glance-registry-dist-paste.ini
%{_unitdir}/openstack-glance-registry.service

%config(noreplace) %attr(-, root, glance) %{_sysconfdir}/glance/glance-registry.conf

%files -n python-glance
%doc README.rst
%license LICENSE
%{python2_sitelib}/glance
%{python2_sitelib}/glance-*.egg-info

%files doc
%license LICENSE
%doc doc/build/html

%changelog
