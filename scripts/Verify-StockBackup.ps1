[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BackupDirectory,
    [switch]$CrossCheckStockLayout
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $BackupDirectory).Path
if (Test-Path -LiteralPath (Join-Path $root 'FAILED.txt')) { throw 'The device recorded a failed backup. Do not flash.' }
$tablePath = Join-Path $root 'proc-mtd.txt'
if (-not (Test-Path -LiteralPath $tablePath)) { throw 'Missing original proc-mtd.txt snapshot.' }
$entries = @()
foreach ($line in Get-Content -Encoding UTF8 -LiteralPath $tablePath) {
    if ($line -match '^mtd(?<index>\d+):\s+(?<size>[a-fA-F0-9]+)\s+(?<erase>[a-fA-F0-9]+)\s+"(?<name>[^"]+)"') {
        $entries += [PSCustomObject]@{index=[int]$Matches.index;size=[Convert]::ToInt64($Matches.size,16);name=$Matches.name;path=$null}
    }
}
if (-not $entries.Count) { throw 'No partitions parsed from proc-mtd.txt.' }
foreach ($name in @('bootloader','romfile','bosa','ri','all_flash')) {
    if (@($entries | Where-Object name -eq $name).Count -ne 1) { throw ('Missing/ambiguous original partition: ' + $name) }
}
$algorithm = $null
$hashPath = $null
foreach ($candidate in @(@('sha256sums.txt','SHA256'),@('md5sums.txt','MD5'),@('md5.txt','MD5'))) {
    $path = Join-Path $root $candidate[0]
    if (Test-Path -LiteralPath $path) { $hashPath=$path; $algorithm=$candidate[1]; break }
}
if (-not $hashPath) { throw 'No device-generated checksum list. PC-only hashes cannot verify the transfer.' }
$expectedHashes = @{}
foreach ($line in Get-Content -Encoding UTF8 -LiteralPath $hashPath) {
    if ($line -match '^(?<hash>[a-fA-F0-9]{32}|[a-fA-F0-9]{64})\s+\*?(?<path>.+)$') {
        $digest = $Matches.hash.ToLowerInvariant()
        $leaf = ($Matches.path -replace '^.*[\\/]','').Trim()
        if ($leaf -match '^mtd(?<index>\d+)(?:[-.].*)?$') { $expectedHashes[[int]$Matches.index] = $digest }
    }
}
foreach ($entry in $entries) {
    $plain = Join-Path $root ('mtd' + $entry.index + '.bin')
    $named = Join-Path $root ('mtd' + $entry.index + '-' + $entry.name + '.bin')
    if (Test-Path -LiteralPath $plain) { $entry.path=$plain }
    elseif (Test-Path -LiteralPath $named) { $entry.path=$named }
    else { throw ('Missing partition file: mtd' + $entry.index + ' (' + $entry.name + ')') }
    if ((Get-Item -LiteralPath $entry.path).Length -ne $entry.size) { throw ('Length mismatch: ' + $entry.name) }
    if (-not $expectedHashes.ContainsKey($entry.index)) { throw ('Missing device checksum: ' + $entry.name) }
    $actual = (Get-FileHash -LiteralPath $entry.path -Algorithm $algorithm).Hash.ToLowerInvariant()
    if ($actual -ne $expectedHashes[$entry.index]) { throw ('Device/PC hash mismatch: ' + $entry.name) }
    Write-Host ('PASS mtd' + $entry.index + ' ' + $entry.name + ' ' + $entry.size + ' bytes')
}
if ($CrossCheckStockLayout) {
    # Known stock critical offsets only. Never derive offsets by summing overlapping views.
    $critical = @(
        @('bootloader',0x0,0x80000),@('romfile',0x80000,0x40000),
        @('bosa',0x51c0000,0x40000),@('ri',0x5200000,0x40000),
        @('flag',0x5240000,0x40000),@('flagback',0x5280000,0x40000)
    )
    $whole = $entries | Where-Object name -eq 'all_flash'
    if ($whole.size -ne 0xeba0000) { throw 'all_flash size differs from the known stock layout; omit this optional check and inspect offsets.' }
    $stream = [IO.File]::OpenRead($whole.path)
    try {
        foreach ($item in $critical) {
            $part = @($entries | Where-Object name -eq $item[0])
            if ($part.Count -ne 1 -or $part[0].size -ne $item[2]) { throw ('Known stock layout not matched: ' + $item[0]) }
            [void]$stream.Seek($item[1],[IO.SeekOrigin]::Begin)
            $buffer = New-Object byte[] $item[2]
            $offset = 0
            while ($offset -lt $buffer.Length) {
                $read = $stream.Read($buffer,$offset,$buffer.Length-$offset)
                if ($read -eq 0) { throw 'Unexpected end of all_flash.' }
                $offset += $read
            }
            $sha = [Security.Cryptography.SHA256]::Create()
            try { $sliceHash = ([BitConverter]::ToString($sha.ComputeHash($buffer))).Replace('-','').ToLowerInvariant() }
            finally { $sha.Dispose() }
            if ($sliceHash -ne (Get-FileHash -LiteralPath $part[0].path -Algorithm SHA256).Hash.ToLowerInvariant()) {
                throw ('Independent partition / all_flash slice mismatch: ' + $item[0] + '. It may have changed during backup; inspect and recapture.')
            }
            Write-Host ('PASS all_flash slice: ' + $item[0])
        }
    } finally { $stream.Dispose() }
}
$logs = @(Get-ChildItem -LiteralPath $root -Filter 'dmesg*.txt')
if ($logs.Count) {
    $hits = @($logs | Select-String -Pattern '(?i)bad\s+(erase)?block|uncorrectable|ecc.{0,30}(fail|error)')
    if ($hits.Count) { Write-Warning 'NAND/ECC messages found. Do not assume a linear all_flash image is safe for a whole-device restore.' }
} else { Write-Warning 'No NAND kernel logs supplied. Bad-block status has not been assessed.' }
Write-Host ('PASS: ' + $entries.Count + ' original partition files match sizes and device-generated checksums.')
Write-Host 'Keep a second independent copy. This does not certify NAND health or a recovery procedure.'
