#!/usr/bin/env bash

set -euo pipefail
shopt -u patsub_replacement 2>/dev/null || true

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$script_dir"
source "$repo_root/scripts/common.sh"

harness_keys=(codex claude-code opencode hermes pi oh-my-pi dsh zcode workbuddy)
harness_labels=(
    "Codex / universal .agents"
    "Claude Code"
    "OpenCode"
    "Hermes"
    "Pi"
    "Oh My Pi"
    "DSH"
    "ZCode"
    "WorkBuddy"
)
harness_paths=(
    "$HOME/.agents/skills/lab-report"
    "$HOME/.claude/skills/lab-report"
    "$HOME/.config/opencode/skills/lab-report"
    "$HOME/.hermes/skills/lab-report"
    "$HOME/.pi/agent/skills/lab-report"
    "$HOME/.omp/agent/skills/lab-report"
    "$HOME/.dsh/skills/lab-report"
    "$HOME/.zcode/skills/lab-report"
    "$HOME/.workbuddy/skills/lab-report"
)

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Install the lab-report skill into one or more user-level harness directories.

Usage:
  bash install.sh [options]

Options:
  --harness LIST            Harness keys separated by commas or spaces.
                            Use "all" for every supported harness.
  --target-path PATH        Install to one custom compatible skill root.
  --student-name NAME       Student name.
  --student-id ID           Student ID.
  --major MAJOR             Major.
  --college COLLEGE         College.
  --wordmark-file PATH      Optional custom wordmark image.
  --seal-file PATH          Optional custom seal image.
  --force                   Back up and replace existing installations.
  --dry-run                 Print selected targets without writing files.
  --help                    Show this help.

Supported harness keys:
  codex, claude-code, opencode, hermes, pi, oh-my-pi, dsh, zcode, workbuddy

Examples:
  bash install.sh --harness codex
  bash install.sh --harness codex,claude-code,opencode
  bash install.sh --harness all --dry-run
EOF
}

append_index() {
    local candidate="$1"
    local existing
    for existing in "${SELECTED_INDICES[@]:-}"; do
        [[ "$existing" == "$candidate" ]] && return 0
    done
    SELECTED_INDICES+=("$candidate")
}

parse_harness_tokens() {
    local tokens=()
    local token index lower all=0
    IFS=', ' read -r -a tokens <<< "$1"

    for token in "${tokens[@]}"; do
        [[ -z "$token" ]] && continue
        lower="$(printf '%s' "$token" | tr '[:upper:]' '[:lower:]')"
        if [[ "$lower" == "all" ]]; then
            all=1
            continue
        fi
        if [[ "$lower" =~ ^[0-9]+$ ]]; then
            index=$((lower - 1))
            if (( index < 0 || index >= ${#harness_keys[@]} )); then
                die "Invalid harness selection: $token"
            fi
            append_index "$index"
            continue
        fi
        for index in "${!harness_keys[@]}"; do
            if [[ "${harness_keys[$index]}" == "$lower" ]]; then
                append_index "$index"
                break
            fi
        done
        if [[ "${harness_keys[$index]:-}" != "$lower" ]]; then
            die "Unknown harness: $token"
        fi
    done

    if (( all == 1 )); then
        SELECTED_INDICES=()
        for index in "${!harness_keys[@]}"; do
            SELECTED_INDICES+=("$index")
        done
    fi
}

select_interactively() {
    local answer token index
    printf '%s\n' 'Install the skill for one or more harnesses:'
    for index in "${!harness_keys[@]}"; do
        printf '  %d. %s\n' "$((index + 1))" "${harness_labels[$index]}"
    done
    printf '  %d. All harnesses\n' "$((${#harness_keys[@]} + 1))"
    read -r -p "Select numbers or names separated by commas (default: 1): " answer || true
    [[ -z "$answer" ]] && answer='1'

    IFS=', ' read -r -a tokens <<< "$answer"
    for token in "${tokens[@]}"; do
        [[ -z "$token" ]] && continue
        if [[ "$token" =~ ^[0-9]+$ ]] && (( token == ${#harness_keys[@]} + 1 )); then
            parse_harness_tokens all
            return 0
        fi
    done
    parse_harness_tokens "$answer"
}

copy_skill_tree() {
    local destination="$1"
    local item name
    mkdir -p "$destination"
    shopt -s dotglob nullglob
    for item in "$repo_root"/*; do
        name="${item##*/}"
        case "$name" in
            .git|.github|.gitattributes|.gitignore|build|reports|output|tmp|docs|AGENTS.md|CHANGELOG.md|personal-profile.json|profile.example.json|install.ps1|install.sh|__pycache__)
                continue
                ;;
        esac
        cp -a -- "$item" "$destination/"
    done
    find "$destination" -type d -name '__pycache__' -prune -exec rm -rf -- {} +
    find "$destination" -type f -name '*.pyc' -delete
}

copy_optional_asset() {
    local source_path="$1"
    local prefix="$2"
    local fallback="$3"
    local asset_dir="$4"

    if [[ -z "$source_path" ]]; then
        printf '%s' "$fallback"
        return 0
    fi

    local base extension filename
    base="$(basename -- "$source_path")"
    if [[ "$base" != *.* ]]; then
        die "Image has no file extension: $source_path"
    fi
    extension="${base##*.}"
    filename="$prefix.$extension"
    cp -- "$source_path" "$asset_dir/$filename"
    printf '%s' "assets/latex/lab-report/assets/$filename"
}

harness_arg=''
target_path=''
student_name=''
student_id=''
major=''
college=''
wordmark_file=''
seal_file=''
force=0
dry_run=0
SELECTED_INDICES=()

while (( $# > 0 )); do
    case "$1" in
        --harness)
            [[ $# -ge 2 ]] || die 'Missing value for --harness.'
            harness_arg="$2"
            shift 2
            ;;
        --harness=*)
            harness_arg="${1#*=}"
            shift
            ;;
        --target-path)
            [[ $# -ge 2 ]] || die 'Missing value for --target-path.'
            target_path="$2"
            shift 2
            ;;
        --target-path=*)
            target_path="${1#*=}"
            shift
            ;;
        --student-name)
            [[ $# -ge 2 ]] || die 'Missing value for --student-name.'
            student_name="$2"
            shift 2
            ;;
        --student-name=*)
            student_name="${1#*=}"
            shift
            ;;
        --student-id)
            [[ $# -ge 2 ]] || die 'Missing value for --student-id.'
            student_id="$2"
            shift 2
            ;;
        --student-id=*)
            student_id="${1#*=}"
            shift
            ;;
        --major)
            [[ $# -ge 2 ]] || die 'Missing value for --major.'
            major="$2"
            shift 2
            ;;
        --major=*)
            major="${1#*=}"
            shift
            ;;
        --college)
            [[ $# -ge 2 ]] || die 'Missing value for --college.'
            college="$2"
            shift 2
            ;;
        --college=*)
            college="${1#*=}"
            shift
            ;;
        --wordmark-file)
            [[ $# -ge 2 ]] || die 'Missing value for --wordmark-file.'
            wordmark_file="$2"
            shift 2
            ;;
        --wordmark-file=*)
            wordmark_file="${1#*=}"
            shift
            ;;
        --seal-file)
            [[ $# -ge 2 ]] || die 'Missing value for --seal-file.'
            seal_file="$2"
            shift 2
            ;;
        --seal-file=*)
            seal_file="${1#*=}"
            shift
            ;;
        --force)
            force=1
            shift
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

if [[ ! -f "$repo_root/SKILL.md" ]]; then
    die "This installer must be run from the shared skill repository root: $repo_root"
fi

if [[ -n "$target_path" ]]; then
    target_labels=("Custom target")
    target_paths=("$(absolute_path "$target_path")")
else
    if [[ -z "$harness_arg" ]]; then
        select_interactively
    else
        parse_harness_tokens "$harness_arg"
    fi

    if (( ${#SELECTED_INDICES[@]} == 0 )); then
        die 'No installation target selected.'
    fi

    target_labels=()
    target_paths=()
    for index in "${SELECTED_INDICES[@]}"; do
        target_labels+=("${harness_labels[$index]}")
        target_paths+=("$(absolute_path "${harness_paths[$index]}")")
    done
fi

if (( dry_run == 1 )); then
    printf '%s\n' 'Dry run: selected installation targets'
    for index in "${!target_paths[@]}"; do
        printf '  %s: %s\n' "${target_labels[$index]}" "${target_paths[$index]}"
    done
    exit 0
fi

existing_targets=()
for target in "${target_paths[@]}"; do
    [[ -e "$target" ]] && existing_targets+=("$target")
done
if (( ${#existing_targets[@]} > 0 && force == 0 )); then
    printf '%s\n' 'Existing skill directories:' >&2
    printf '  - %s\n' "${existing_targets[@]}" >&2
    die 'Target already exists. Use --force to back up and replace existing installations.'
fi

if [[ -z "$student_name" ]]; then
    read -r -p 'Student name: ' student_name || true
fi
if [[ -z "$student_id" ]]; then
    read -r -p 'Student ID: ' student_id || true
fi
if [[ -z "$major" ]]; then
    read -r -p 'Major (optional): ' major || true
fi
if [[ -z "$college" ]]; then
    read -r -p 'College (optional): ' college || true
fi
if [[ -z "$wordmark_file" ]]; then
    read -r -p 'University wordmark image path (optional): ' wordmark_file || true
fi
if [[ -z "$seal_file" ]]; then
    read -r -p 'University seal/logo image path (optional): ' seal_file || true
fi

[[ -n "$student_name" ]] || die 'Student name and student ID are required.'
[[ -n "$student_id" ]] || die 'Student name and student ID are required.'

wordmark_source=''
seal_source=''
if [[ -n "$wordmark_file" ]]; then
    wordmark_source="$(absolute_path "$wordmark_file")"
    [[ -f "$wordmark_source" ]] || die "Image file not found: $wordmark_source"
fi
if [[ -n "$seal_file" ]]; then
    seal_source="$(absolute_path "$seal_file")"
    [[ -f "$seal_source" ]] || die "Image file not found: $seal_source"
fi

for index in "${!target_paths[@]}"; do
    target="${target_paths[$index]}"
    if [[ -e "$target" ]]; then
        backup="$target.backup-$(date +%Y%m%d-%H%M%S)"
        mv -- "$target" "$backup"
        printf 'Existing skill backed up to: %s\n' "$backup"
    fi

    copy_skill_tree "$target"
    chmod +x "$target/scripts/"*.sh 2>/dev/null || true

    asset_dir="$target/assets/latex/lab-report/assets"
    mkdir -p "$asset_dir"
    wordmark_relative="$(copy_optional_asset "$wordmark_source" 'custom-wordmark' 'assets/latex/lab-report/assets/university_wordmark.png' "$asset_dir")"
    seal_relative="$(copy_optional_asset "$seal_source" 'custom-seal' 'assets/latex/lab-report/assets/university_logo.jpeg' "$asset_dir")"
    installed_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    {
        printf '{\n'
        printf '  "student_name": "%s",\n' "$(json_escape "$student_name")"
        printf '  "student_id": "%s",\n' "$(json_escape "$student_id")"
        printf '  "major": "%s",\n' "$(json_escape "$major")"
        printf '  "college": "%s",\n' "$(json_escape "$college")"
        printf '  "wordmark_file": "%s",\n' "$(json_escape "$wordmark_relative")"
        printf '  "seal_file": "%s",\n' "$(json_escape "$seal_relative")"
        printf '  "installed_at": "%s"\n' "$(json_escape "$installed_at")"
        printf '}\n'
    } > "$target/personal-profile.json"

    printf 'Installed personalized skill: %s\n' "$target"
done

printf '\nInstalled skill name: lab-report\n'
printf '%s\n' 'Open your selected harness and ask it to use lab-report, or use its native skill command if available.'
printf '%s\n' 'Personal details are stored only in each target skill directory under personal-profile.json.'
