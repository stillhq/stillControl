Name:           stillcontrol
Version:        0.1
Release:        1%{?dist}
Summary:        Used for customing stillOS. Replaces GNOME Tweaks, Extension Manager, and more.

License:        GPL v3
URL:            https://github.com/stillHQ/stillControl
Source0:        %{url}/archive/refs/heads/main.tar.gz
BuildArch:      noarch

Requires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%description
stillControl is a tool used for customizing stillOS. It replaces GNOME Tweaks, Extension Manager, and more.
Some features include:
  - A layout switcher
  - Integration with Dash to Panel, Dash to Dock, and Arc Menu
  - Extension Manager

%prep
%autosetup -n stillControl-main

%build
%install
mkdir -p %{buildroot}%{python3_sitelib}/stillControl/data
mkdir -p %{buildroot}%{python3_sitelib}/stillControl/layouts
mkdir -p %{buildroot}%{python3_sitelib}/stillControl/UIs
mkdir -p %{buildroot}%{_bindir}
install -d -m 0755 src/__main__.py %{buildroot}%{_bindir}/stillcontrol
install -m 0755 src %{buildroot}%{python3_sitelib}/stillControl

%files
%doc README.md
%{python3_sitelib}/stillControl

%changelog
*  Tue Jul 30 2024 Cameron Knauff <cameron@stillhq.io> - 0.1
- First build, big!