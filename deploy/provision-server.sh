#!/usr/bin/env bash
# Provisions the website's tenant on the shared production host. Run as root, from a copy of
# this directory, with the public half of the GitHub Actions deploy key:
#
#   sudo ./provision-server.sh ./status-effects-deploy ./deploy-key.pub
#
# It creates only what belongs to this tenant and can be run again (e.g. to install a changed
# deploy command or a new key):
#
#   se-deploy                                  locked account, no sudo, no extra groups
#   its rootless Docker daemon                 user service, started at boot (lingering)
#   /srv/status-effects/                       repository mirror, releases, state
#   /etc/status-effects/                       private configuration (the tunnel token)
#   /usr/local/libexec/status-effects-deploy   root-owned forced command of the deploy key
#   /home/se-deploy/.ssh/authorized_keys       the deploy key, restricted to that command
#
# It installs no package and changes no host-wide setting (SSH daemon, firewall, system Docker,
# other accounts); when the host lacks something it stops and says what.
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C

readonly ACCOUNT=se-deploy
readonly ACCOUNT_HOME="/home/$ACCOUNT"
readonly STATE_ROOT=/srv/status-effects
readonly PRIVATE_ROOT=/etc/status-effects
readonly COMMAND_PATH=/usr/local/libexec/status-effects-deploy

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

(($# == 2)) || die "usage: $0 <status-effects-deploy> <deploy-key.pub>"
# Absolute, because the account's commands below run from /.
command_source="$(realpath -- "$1")"
key_source="$(realpath -- "$2")"
readonly command_source key_source

#----------------------------------------------------------------------------------------------
# Preflight: nothing is changed before all of this holds
#----------------------------------------------------------------------------------------------

((EUID == 0)) || die "run as root"
# shellcheck source=/dev/null
. /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || die "expected Ubuntu"

for tool in docker dockerd-rootless-setuptool.sh rootlesskit newuidmap newgidmap git flock tar loginctl runuser nsenter; do
  command -v "$tool" >/dev/null || die "the host has no '$tool' (ask the owner before installing anything host-wide)"
done
docker compose version >/dev/null 2>&1 || die "the host has no Docker Compose plugin"

[[ -f "$command_source" ]] || die "no such file: $command_source"
bash -n "$command_source" || die "$command_source is not a valid script"

[[ -f "$key_source" ]] || die "no such file: $key_source"
(($(grep -c . "$key_source") == 1)) || die "$key_source must hold exactly one public key"
read -r key_type key_blob _ <"$key_source"
[[ "$key_type" == "ssh-ed25519" && "$key_blob" =~ ^[A-Za-z0-9+/=]+$ ]] || die "expected one ssh-ed25519 public key"
ssh-keygen -l -f "$key_source" >/dev/null || die "$key_source is not a valid public key"

#----------------------------------------------------------------------------------------------
# Account: locked password, private group only, own subordinate ID range
#----------------------------------------------------------------------------------------------

if ! id "$ACCOUNT" >/dev/null 2>&1; then
  useradd --create-home --home-dir "$ACCOUNT_HOME" --shell /bin/bash --user-group "$ACCOUNT"
fi
usermod --lock "$ACCOUNT"
chmod 0700 "$ACCOUNT_HOME"

[[ "$(id -Gn "$ACCOUNT")" == "$ACCOUNT" ]] || die "$ACCOUNT must not be in any supplementary group"
grep -Eq "^$ACCOUNT:[0-9]+:65536$" /etc/subuid || die "$ACCOUNT has no subordinate UID range in /etc/subuid"
grep -Eq "^$ACCOUNT:[0-9]+:65536$" /etc/subgid || die "$ACCOUNT has no subordinate GID range in /etc/subgid"
account_uid="$(id -u "$ACCOUNT")"
readonly account_uid

#----------------------------------------------------------------------------------------------
# Directories. The private one must exist before the rootless daemon starts: RootlessKit copies
# /etc into the daemon's mount namespace at that moment, and a directory created later would be
# invisible to bind mounts (the tunnel token secret) until the daemon restarts.
#----------------------------------------------------------------------------------------------

install -d -m 0750 -o root -g "$ACCOUNT" "$STATE_ROOT"
install -d -m 0700 -o "$ACCOUNT" -g "$ACCOUNT" \
  "$STATE_ROOT/repository" "$STATE_ROOT/releases" "$STATE_ROOT/state"
install -d -m 0700 -o "$ACCOUNT" -g "$ACCOUNT" "$PRIVATE_ROOT"

#----------------------------------------------------------------------------------------------
# Rootless Docker daemon of the account, kept running across reboots by lingering
#----------------------------------------------------------------------------------------------

loginctl enable-linger "$ACCOUNT"
for _ in $(seq 1 30); do
  [[ -S "/run/user/$account_uid/bus" ]] && break
  sleep 1
done
[[ -S "/run/user/$account_uid/bus" ]] || die "the systemd user manager of $ACCOUNT did not start"

as_account=(
  runuser -u "$ACCOUNT" -- env
  HOME="$ACCOUNT_HOME"
  USER="$ACCOUNT"
  LOGNAME="$ACCOUNT"
  XDG_RUNTIME_DIR="/run/user/$account_uid"
  DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$account_uid/bus"
  DOCKER_HOST="unix:///run/user/$account_uid/docker.sock"
  PATH=/usr/local/bin:/usr/bin:/bin
)
cd /

if [[ ! -f "$ACCOUNT_HOME/.config/systemd/user/docker.service" ]]; then
  "${as_account[@]}" dockerd-rootless-setuptool.sh install
fi
"${as_account[@]}" systemctl --user enable --now docker.service

for _ in $(seq 1 30); do
  "${as_account[@]}" docker info >/dev/null 2>&1 && break
  sleep 1
done
"${as_account[@]}" docker info --format '{{json .SecurityOptions}}' | grep -Fq 'name=rootless' ||
  die "the Docker daemon of $ACCOUNT does not report rootless mode"

daemon_pid="$(<"/run/user/$account_uid/dockerd-rootless/child_pid")"
[[ "$daemon_pid" =~ ^[1-9][0-9]*$ ]] || die "cannot find the rootless daemon process"
runuser -u "$ACCOUNT" -- nsenter --user --preserve-credentials --mount --target "$daemon_pid" \
  test -d "$PRIVATE_ROOT" || die "the rootless daemon cannot see $PRIVATE_ROOT; restart its docker.service"

#----------------------------------------------------------------------------------------------
# Deploy command and the key that may run nothing else
#----------------------------------------------------------------------------------------------

[[ -d /usr/local/libexec ]] || install -d -m 0755 -o root -g root /usr/local/libexec
install -m 0755 -o root -g root "$command_source" "$COMMAND_PATH"

install -d -m 0700 -o "$ACCOUNT" -g "$ACCOUNT" "$ACCOUNT_HOME/.ssh"
authorized_keys="$ACCOUNT_HOME/.ssh/authorized_keys"
printf 'command="%s",restrict %s %s status-effects-github-actions\n' "$COMMAND_PATH" "$key_type" "$key_blob" \
  >"$authorized_keys.new"
chown "$ACCOUNT:$ACCOUNT" "$authorized_keys.new"
chmod 0600 "$authorized_keys.new"
mv -- "$authorized_keys.new" "$authorized_keys"

#----------------------------------------------------------------------------------------------
# Summary (metadata only)
#----------------------------------------------------------------------------------------------

echo "Provisioned:"
id "$ACCOUNT"
passwd --status "$ACCOUNT" | awk '{print "password status: " $2}'
grep -E "^$ACCOUNT:" /etc/subuid | sed 's/^/subuid: /'
stat -c '%a %U:%G %n' "$ACCOUNT_HOME" "$ACCOUNT_HOME/.ssh" "$authorized_keys" \
  "$STATE_ROOT" "$STATE_ROOT"/* "$PRIVATE_ROOT" "$COMMAND_PATH"
"${as_account[@]}" docker info --format 'docker {{.ServerVersion}}, {{.CgroupDriver}} cgroup driver, cgroup v{{.CgroupVersion}}'
