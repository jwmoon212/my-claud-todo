#!/usr/bin/env bash
# organize_downloads.sh
# Organizes ~/Downloads: images → Pictures, PDFs → Documents, old files → Archive
# Runs a dry-run first, then prompts before moving anything.

SOURCE="$HOME/Downloads"
PICTURES="$SOURCE/Pictures"
DOCUMENTS="$SOURCE/Documents"
ARCHIVE="$SOURCE/Archive"

IMAGE_EXTS=("jpg" "jpeg" "png" "gif" "bmp" "tiff" "webp" "svg" "ico")
CUTOFF_DAYS=30

# ── helpers ────────────────────────────────────────────────────────────────────

is_image() {
    local ext="${1,,}"   # lowercase
    for e in "${IMAGE_EXTS[@]}"; do [[ "$ext" == "$e" ]] && return 0; done
    return 1
}

unique_target() {
    # If $1 already exists, append _1, _2, … until the path is free
    local target="$1"
    if [[ ! -e "$target" ]]; then echo "$target"; return; fi
    local dir; dir="$(dirname "$target")"
    local base; base="$(basename "${target%.*}")"
    local ext="${target##*.}"; [[ "$ext" == "$base" ]] && ext=""  # no extension
    [[ -n "$ext" ]] && ext=".$ext"
    local n=1
    while [[ -e "$dir/${base}_${n}${ext}" ]]; do (( n++ )); done
    echo "$dir/${base}_${n}${ext}"
}

# ── collect moves ──────────────────────────────────────────────────────────────

declare -a FILE_NAMES FROM_PATHS TO_PATHS DEST_DIRS REASONS

while IFS= read -r -d '' filepath; do
    filename="$(basename "$filepath")"
    ext="${filename##*.}"; [[ "$filename" == "$ext" ]] && ext=""  # no extension
    ext="${ext,,}"

    dest=""
    reason=""

    if is_image "$ext"; then
        dest="$PICTURES"; reason="image"
    elif [[ "$ext" == "pdf" ]]; then
        dest="$DOCUMENTS"; reason="PDF"
    else
        # file older than CUTOFF_DAYS?
        if [[ "$(uname)" == "Darwin" ]]; then
            file_mtime=$(stat -f "%m" "$filepath")
        else
            file_mtime=$(stat -c "%Y" "$filepath")
        fi
        cutoff_ts=$(date -d "-${CUTOFF_DAYS} days" +%s 2>/dev/null \
                    || date -v "-${CUTOFF_DAYS}d" +%s)   # macOS fallback
        if (( file_mtime < cutoff_ts )); then
            dest="$ARCHIVE"; reason="older than ${CUTOFF_DAYS} days"
        fi
    fi

    [[ -z "$dest" ]] && continue

    FILE_NAMES+=("$filename")
    FROM_PATHS+=("$filepath")
    TO_PATHS+=("$dest/$filename")
    DEST_DIRS+=("$dest")
    REASONS+=("$reason")

done < <(find "$SOURCE" -maxdepth 1 -type f -print0)

# ── dry-run report ─────────────────────────────────────────────────────────────

total="${#FILE_NAMES[@]}"

if (( total == 0 )); then
    echo "Nothing to move."
    exit 0
fi

echo ""
echo -e "\033[0;36m=== DRY RUN — nothing has been moved yet ===\033[0m"
echo ""

for label in "Pictures" "Documents" "Archive"; do
    dest_path="$SOURCE/$label"
    # collect indices for this destination
    indices=()
    for i in "${!DEST_DIRS[@]}"; do
        [[ "${DEST_DIRS[$i]}" == "$dest_path" ]] && indices+=("$i")
    done
    (( ${#indices[@]} == 0 )) && continue

    echo -e "\033[0;33m[$label]  (${#indices[@]} file(s))\033[0m"
    for i in "${indices[@]}"; do
        echo "  ${FILE_NAMES[$i]}  [${REASONS[$i]}]"
    done
    echo ""
done

echo -e "\033[0;36mTotal: $total file(s) will be moved.\033[0m"
echo ""

# ── confirm ────────────────────────────────────────────────────────────────────

read -r -p "Proceed? (yes/no) " answer
answer="${answer,,}"
if [[ "$answer" != "yes" && "$answer" != "y" ]]; then
    echo -e "\033[0;31mAborted. No files were moved.\033[0m"
    exit 0
fi

# ── move ───────────────────────────────────────────────────────────────────────

for dir in "$PICTURES" "$DOCUMENTS" "$ARCHIVE"; do
    mkdir -p "$dir"
done

moved=0; errors=0

for i in "${!FILE_NAMES[@]}"; do
    target="$(unique_target "${TO_PATHS[$i]}")"
    label="$(basename "${DEST_DIRS[$i]}")"
    if mv "${FROM_PATHS[$i]}" "$target"; then
        echo -e "\033[0;32mMoved: ${FILE_NAMES[$i]} → $label\033[0m"
        (( moved++ ))
    else
        echo -e "\033[0;31mERROR moving ${FILE_NAMES[$i]}\033[0m"
        (( errors++ ))
    fi
done

echo ""
echo -e "\033[0;36mDone. $moved moved, $errors error(s).\033[0m"
