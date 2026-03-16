#!/usr/bin/env bash
set -euo pipefail

tmp_bin_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_bin_dir"
}
trap cleanup EXIT

# Avoid installer sudo prompts for optional ripgrep/ffmpeg in headless runs.
if ! command -v rg >/dev/null 2>&1; then
  cat > "$tmp_bin_dir/rg" <<'EOF'
#!/usr/bin/env bash
echo 'ripgrep 0.0.0 (shim)'
EOF
  chmod +x "$tmp_bin_dir/rg"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  cat > "$tmp_bin_dir/ffmpeg" <<'EOF'
#!/usr/bin/env bash
echo 'ffmpeg version 0.0.0-shim'
EOF
  chmod +x "$tmp_bin_dir/ffmpeg"
fi

# Avoid sudo password prompts in headless install; attempts run without elevation.
cat > "$tmp_bin_dir/sudo" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = "-n" ] && [ "${2:-}" = "true" ]; then
  exit 0
fi
if [ "${1:-}" = "-n" ]; then
  shift
fi
while [ $# -gt 0 ] && [[ "$1" == *=* ]]; do
  export "$1"
  shift
done
exec "$@"
EOF
chmod +x "$tmp_bin_dir/sudo"

export PATH="$tmp_bin_dir:$PATH"

if command -v setsid >/dev/null 2>&1; then
  setsid -w bash -lc 'curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-setup' </dev/null
else
  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-setup
fi
