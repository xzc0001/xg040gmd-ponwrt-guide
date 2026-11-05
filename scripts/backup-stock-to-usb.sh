#!/bin/sh
# Reads MTD character devices and writes only to a mounted USB/SD filesystem.
# Usage: sh backup-stock-to-usb.sh /mnt/UDISK
# Does not erase/write MTD, change settings, unmount media, or reboot.
set -eu
fail() { printf 'STOP: %s\n' "$*" >&2; exit 1; }
[ "$(id -u)" = 0 ] || fail 'Root shell required.'
[ "$#" = 1 ] || fail 'Pass the actual USB mount root, e.g. /mnt/UDISK.'
mount_root=$(cd "$1" 2>/dev/null && pwd -P) || fail 'Mount path does not exist.'
awk -v p="$mount_root" '$2 == p && $1 ~ /^\/dev\/(sd|mmcblk)/ {ok=1} END {exit !ok}' /proc/mounts ||
    fail 'Path is not an exact mounted USB/SD root. Check /proc/mounts; never use /tmp.'
[ -w "$mount_root" ] || fail 'Mounted filesystem is not writable.'
for name in bootloader romfile bosa ri all_flash; do
    grep -q "\"$name\"" /proc/mtd || fail "Missing original partition: $name. Inspect the layout first."
done
if command -v sha256sum >/dev/null 2>&1; then
    hash_tool=sha256sum
    hash_file=sha256sums.txt
elif command -v md5sum >/dev/null 2>&1; then
    hash_tool=md5sum
    hash_file=md5sums.txt
else
    fail 'No on-device hash tool. Do not proceed without copy verification.'
fi
required=0
while read -r mtd size_hex erase_hex rest; do
    case "$mtd" in mtd[0-9]*:) ;; *) continue ;; esac
    required=$((required + 0x$size_hex))
done < /proc/mtd
available_kb=$(df -Pk "$mount_root" | awk 'NR==2 {print $4}')
case "$available_kb" in ''|*[!0-9]*) fail 'Cannot determine USB free space.' ;; esac
[ "$((available_kb * 1024))" -ge "$((required + 33554432))" ] || fail 'Not enough USB space for every MTD view plus 32 MiB.'
stamp=$(date '+%Y%m%d-%H%M%S')
out="$mount_root/xg040gmd-stock-$stamp-$$"
mkdir "$out" || fail 'Cannot create a fresh backup directory.'
cat /proc/mtd > "$out/proc-mtd.txt"
cat /proc/mounts > "$out/proc-mounts.txt"
uname -a > "$out/uname.txt"
dmesg > "$out/dmesg-before.txt" 2>&1 || :
awk '/^mtd[0-9]+:/ {n=$1;sub(/:$/,"",n); name=$4;gsub(/\"/,"",name);print n,$2,$3,name}' /proc/mtd > "$out/mtd-expected.tsv"
: > "$out/$hash_file"
while read -r mtd size_hex erase_hex name; do
    [ -c "/dev/$mtd" ] || fail "Missing MTD character device: /dev/$mtd; incomplete backup in $out"
    expected=$((0x$size_hex))
    printf 'Reading %s (%s), expected %s bytes\n' "$mtd" "$name" "$expected"
    if ! dd "if=/dev/$mtd" "of=$out/$mtd.bin" bs=131072 2> "$out/$mtd-read.log"; then
        cat "$out/$mtd-read.log" >&2
        printf 'MTD read failed: %s\n' "$mtd" > "$out/FAILED.txt"
        sync
        fail "Read error. Keep the incomplete evidence; do not flash. $out"
    fi
    bytes=$(wc -c < "$out/$mtd.bin")
    if [ "$bytes" -ne "$expected" ]; then
        printf '%s length mismatch: %s / %s\n' "$mtd" "$bytes" "$expected" > "$out/FAILED.txt"
        sync
        fail 'Short read. Do not flash.'
    fi
    (cd "$out" && "$hash_tool" "$mtd.bin") >> "$out/$hash_file"
done < "$out/mtd-expected.tsv"
dmesg > "$out/dmesg-after.txt" 2>&1 || :
printf 'All listed MTD views copied; sizes checked; device-side hashes generated.\nRun Verify-StockBackup.ps1 on the PC. Hardware recovery readiness is not certified.\n' > "$out/COMPLETE.txt"
sync
printf '\nBackup stored on USB: %s\n' "$out"
printf 'Copy this entire folder to the PC, verify it, and keep a second independent copy.\n'
printf 'No MTD write, erase, configuration change, or reboot was performed.\n'
