#!/bin/sh
# Read-only inspection. Run in the original firmware shell, not on Windows.
printf '\n=== identity and kernel ===\n'
id
uname -a
printf '\n=== CPU and memory ===\n'
cat /proc/cpuinfo
cat /proc/meminfo
printf '\n=== original MTD table ===\n'
cat /proc/mtd
printf '\n=== mounts and free space ===\n'
cat /proc/mounts
df -k
printf '\n=== MTD geometry, offsets, and ECC counters when available ===\n'
for d in /sys/class/mtd/mtd[0-9]*; do
    [ -d "$d" ] || continue
    case "$d" in *ro) continue ;; esac
    printf '%s\n' "$d"
    for f in name size erasesize writesize oobsize offset bad_blocks corrected_bits ecc_failures; do
        [ -r "$d/$f" ] || continue
        printf '  %s=' "$f"
        cat "$d/$f"
    done
done
printf '\n=== available transfer/checksum tools ===\n'
for tool in dd sha256sum md5sum wget tftp nc nanddump mtd_debug; do
    command -v "$tool" 2>/dev/null || :
done
printf '\n=== NAND and ECC kernel messages ===\n'
dmesg | grep -iE 'nand|spinand|spi-nand|skyhigh|fudan|s35ml|fm25|bad|ecc|uncorrect'
printf '\n=== end; no flash write performed ===\n'
