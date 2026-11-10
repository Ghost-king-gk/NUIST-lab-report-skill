[CmdletBinding()]
param(
    [string]$TargetPath = (Join-Path $HOME '.agents\skills\lab-report'),
    [string]$StudentName = '',
    [string]$StudentID = '',
    [string]$Major = '',
    [string]$College = '',
    [string]$WordmarkFile = '',
    [string]$SealFile = '',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$target = [System.IO.Path]::GetFullPath($TargetPath)

if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'SKILL.md') -PathType Leaf)) {
    throw "This installer must be run from the shared skill repository root: $repoRoot"
}

if (Test-Path -LiteralPath $target) {
    if (-not $Force) {
        throw "Target already exists: $target. Use -Force to replace it; the existing folder will be backed up first."
    }
    $backup = "$target.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $target -Destination $backup
    Write-Host "Existing skill backed up to: $backup" -ForegroundColor Yellow
}

if ([string]::IsNullOrWhiteSpace($StudentName)) { $StudentName = Read-Host 'Student name' }
if ([string]::IsNullOrWhiteSpace($StudentID)) { $StudentID = Read-Host 'Student ID' }
if ([string]::IsNullOrWhiteSpace($Major)) { $Major = Read-Host 'Major (optional)' }
if ([string]::IsNullOrWhiteSpace($College)) { $College = Read-Host 'College or institution (optional)' }
if ([string]::IsNullOrWhiteSpace($WordmarkFile)) {
    $WordmarkFile = Read-Host 'University wordmark image path (optional; Enter uses placeholder)'
}
if ([string]::IsNullOrWhiteSpace($SealFile)) {
    $SealFile = Read-Host 'University seal/logo image path (optional; Enter uses placeholder)'
}
if ([string]::IsNullOrWhiteSpace($StudentName) -or [string]::IsNullOrWhiteSpace($StudentID)) {
    throw 'Student name and student ID are required.'
}

$exclude = @('.git', '.github', 'build', 'tmp', 'docs', 'personal-profile.json', 'profile.example.json', 'install.ps1')
New-Item -ItemType Directory -Force -Path $target | Out-Null
foreach ($item in Get-ChildItem -LiteralPath $repoRoot -Force) {
    if ($exclude -contains $item.Name) { continue }
    $destination = Join-Path $target $item.Name
    if ($item.PSIsContainer) {
        Copy-Item -LiteralPath $item.FullName -Destination $destination -Recurse -Force
    } else {
        Copy-Item -LiteralPath $item.FullName -Destination $destination -Force
    }
}

$assetDir = Join-Path $target 'assets\latex\lab-report\assets'
New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

function Copy-PersonalAsset([string]$source, [string]$prefix, [string]$fallback) {
    if ([string]::IsNullOrWhiteSpace($source)) { return $fallback }
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Image file not found: $source"
    }
    $resolved = [System.IO.Path]::GetFullPath($source)
    $extension = [System.IO.Path]::GetExtension($resolved)
    if ([string]::IsNullOrWhiteSpace($extension)) { throw "Image has no file extension: $source" }
    $filename = "$prefix$extension"
    Copy-Item -LiteralPath $resolved -Destination (Join-Path $assetDir $filename) -Force
    return "assets/latex/lab-report/assets/$filename"
}

$wordmarkRelative = Copy-PersonalAsset $WordmarkFile 'custom-wordmark' 'assets/latex/lab-report/assets/university_wordmark.png'
$sealRelative = Copy-PersonalAsset $SealFile 'custom-seal' 'assets/latex/lab-report/assets/university_logo.jpeg'

$profile = [ordered]@{
    student_name = $StudentName
    student_id = $StudentID
    major = $Major
    college = $College
    wordmark_file = $wordmarkRelative
    seal_file = $sealRelative
    installed_at = (Get-Date).ToString('o')
}
$profile | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $target 'personal-profile.json') -Encoding utf8

Write-Host "Installed personalized skill: $target" -ForegroundColor Green
Write-Host 'Personal details were written only to personal-profile.json inside the target skill.'
Write-Host 'Use: $lab-report' -ForegroundColor Green
