%define name ttyio3
%define version 202001222056
%define unmangled_version 202001222056
%define release 1

Summary: UNKNOWN
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: zoid technologies <ttyio3@projects.zoidtechnologies.com>
Url: http://repo.zoidtechnologies.com/ttyio3/

%description
terminal input and output functions.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
