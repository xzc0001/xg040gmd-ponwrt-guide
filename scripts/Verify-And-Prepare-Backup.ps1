[CmdletBinding()]
param(
    [string]$BackupDirectory,
    [string]$KitRoot
)
$ErrorActionPreference='Stop'
if(-not $KitRoot){$KitRoot=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
if(-not $BackupDirectory){$BackupDirectory=Read-Host 'Paste the complete xg040gmd-stock backup folder path'}
$BackupDirectory=$BackupDirectory.Trim().Trim('"')
$source=(Resolve-Path -LiteralPath $BackupDirectory).Path
$kit=(Resolve-Path -LiteralPath $KitRoot).Path
$stamp=(Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+$PID
$logRoot=Join-Path $kit 'logs'
[void](New-Item -ItemType Directory -Force -Path $logRoot)
$logPath=Join-Path $logRoot ('backup-check-'+$stamp+'.txt')
$transcript=$false
try {
    Start-Transcript -LiteralPath $logPath | Out-Null
    $transcript=$true
    if(-not (Test-Path -LiteralPath (Join-Path $source 'COMPLETE.txt'))){throw 'Missing COMPLETE.txt. This entry expects a completed USB-script backup; keep the evidence and inspect the original read.'}
    & (Join-Path $kit 'scripts\Verify-StockBackup.ps1') -BackupDirectory $source
    $parts=@{}
    foreach($line in Get-Content -Encoding UTF8 -LiteralPath (Join-Path $source 'proc-mtd.txt')) {
        if($line -match '^mtd(?<idx>\d+):\s+(?<size>[0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+"(?<name>[^"]+)"') {
            if($parts.ContainsKey($Matches.name)){throw 'Ambiguous partition name.'}
            $parts[$Matches.name]=[PSCustomObject]@{index=[int]$Matches.idx;size=[Convert]::ToInt64($Matches.size,16)}
        }
    }
    foreach($name in @('bosa','ri')) {
        if(-not $parts.ContainsKey($name) -or $parts[$name].size -ne 262144){throw ('Backup hash check passed, but '+$name+' differs from standard MD board-data size. No automatic export; inspect the actual layout.')}
    }
    $export=Join-Path $kit ('backup\BOARD-DATA\'+(Split-Path -Leaf $source)+'-'+$stamp)
    [void](New-Item -ItemType Directory -Path $export)
    $records=@()
    foreach($name in @('bosa','ri')) {
        $index=$parts[$name].index
        $path=Join-Path $source ('mtd'+$index+'.bin')
        if(-not (Test-Path -LiteralPath $path)){$path=Join-Path $source ('mtd'+$index+'-'+$name+'.bin')}
        $target=Join-Path $export ($name+'.bin')
        Copy-Item -LiteralPath $path -Destination $target
        $digest=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $digest){throw 'Board-data copy hash mismatch.'}
        $records+=[PSCustomObject]@{partition=$name;original_file=$path;export_file=($name+'.bin');bytes=$parts[$name].size;sha256=$digest}
    }
    [PSCustomObject]@{source_backup=$source;created_at=(Get-Date).ToString('o');transfer_validation='original partition sizes and device checksums passed';nand_health_certified=$false;recovery_layout_certified=$false;files=$records} | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $export 'SOURCE-RECORD.json')
    Write-Host ''
    Write-Host ('BOARD-DATA exported: '+$export)
    Write-Host ('Validation transcript: '+$logPath)
    Write-Host 'BACKUP VERIFIED: keep a second independent copy, then continue at step 09 of the full guide. No router was accessed or flashed.'
    Write-Host 'Hash PASS does not certify NAND health, whole-flash restoration, or operator compatibility.'
} finally {
    if($transcript){Stop-Transcript | Out-Null}
}
