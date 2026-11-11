#!/usr/bin/env bash

# Shared helpers for the Bash and WSL entry points. This file is sourced, not executed.

to_linux_path() {
    local value="$1"

    if [[ "$value" =~ ^[A-Za-z]:[\\/] ]]; then
        if command -v wslpath >/dev/null 2>&1; then
            wslpath -u "$value"
            return 0
        fi
        printf '%s\n' "$value"
        return 0
    fi

    printf '%s\n' "$value"
}

absolute_path() {
    local value
    value="$(to_linux_path "$1")"

    if [[ "$value" != /* ]]; then
        value="$PWD/$value"
    fi

    if command -v realpath >/dev/null 2>&1; then
        realpath -m -- "$value"
    else
        printf '%s\n' "$value"
    fi
}

json_escape() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/\\t/g' -e 's/\r/\\r/g'
}

profile_value() {
    local profile_path="$1"
    local key="$2"

    if [[ ! -f "$profile_path" ]]; then
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$profile_path" "$key" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
value = data.get(sys.argv[2], "")
if value is None:
    value = ""
print(value)
PY
        return 0
    fi

    sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\(.*\)\"[[:space:]]*,\{0,1\}$/\1/p" "$profile_path" | head -n 1
}

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'Required command not found: %s\n' "$command_name" >&2
        exit 1
    fi
}
