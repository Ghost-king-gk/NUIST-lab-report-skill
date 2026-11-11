[CmdletBinding()]
param(
    [ValidateSet('codex','claude-code','opencode','hermes','pi','oh-my-pi','dsh','zcode','workbuddy','all')]
    [string[]]$Harness = @(),
    [string]$TargetPath = '',
    [string]$StudentName = '',
    [string]$StudentID = '',
    [string]$Major = '',
    [string]$College = '',
    [string]$WordmarkFile = '',
    [string]$SealFile = '',
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'SKILL.md') -PathType Leaf)) {
    throw "This installer must be run from the shared skill repository root: $repoRoot"
}

$harnessDefinitions = @(
    [pscustomobject]@{ Key = 'codex';       Label = 'Codex / universal .agents'; Path = (Join-Path $HOME '.agents\skills\lab-report') },
    [pscustomobject]@{ Key = 'claude-code'; Label = 'Claude Code';               Path = (Join-Path $HOME '.claude\skills\lab-report') },
    [pscustomobject]@{ Key = 'opencode';     Label = 'OpenCode';                  Path = (Join-Path $HOME '.config\opencode\skills\lab-report') },
    [pscustomobject]@{ Key = 'hermes';       Label = 'Hermes';                    Path = (Join-Path $HOME '.hermes\skills\lab-report') },
    [pscustomobject]@{ Key = 'pi';           Label = 'Pi';                        Path = (Join-Path $HOME '.pi\agent\skills\lab-report') },
    [pscustomobject]@{ Key = 'oh-my-pi';     Label = 'Oh My Pi';                  Path = (Join-Path $HOME '.omp\agent\skills\lab-report') },
    [pscustomobject]@{ Key = 'dsh';          Label = 'DSH';                       Path = (Join-Path $HOME '.dsh\skills\lab-report') },
    [pscustomobject]@{ Key = 'zcode';        Label = 'ZCode';                     Path = (Join-Path $HOME '.zcode\skills\lab-report') },
    [pscustomobject]@{ Key = 'workbuddy';    Label = 'WorkBuddy';                 Path = (Join-Path $HOME '.workbuddy\skills\lab-report') }
)

function Select-Harnesses {
    Write-Host 'Install the skill for one or more harnesses:' -ForegroundColor Cyan
    for ($i = 0; $i -lt $harnessDefinitions.Count; $i++) {
        Write-Host ("  {0}. {1}" -f ($i + 1), $harnessDefinitions[$i].Label)
    }
    Write-Host ("  {0}. All harnesses" -f ($harnessDefinitions.Count + 1))
    $answer = Read-Host 'Select numbers or names separated by commas (default: 1)'
    if ([string]::IsNullOrWhiteSpace($answer)) { $answer = '1' }

    $selected = @()
    foreach ($token in ($answer -split '[,\s]+' | Where-Object { $_ })) {
        if ($token -match '^\d+$') {
            $number = [int]$token
            if ($number -eq ($harnessDefinitions.Count + 1)) {
                return @($harnessDefinitions)
            }
            if ($number -lt 1 -or $number -gt $harnessDefinitions.Count) {
                throw "Invalid harness selection: $token"
            }
            $selected += $harnessDefinitions[$number - 1]
            continue
        }
        if ($token -eq 'all') {
            return @($harnessDefinitions)
        }
        $match = $harnessDefinitions | Where-Object { $_.Key -eq $token -or $_.Label -eq $token }
        if (-not $match) { throw "Unknown harness: $token" }
        $selected += $match
    }
    return @($selected)
}

if (-not [string]::IsNullOrWhiteSpace($TargetPath)) {
    $targets = @([pscustomobject]@{ Key = 'custom'; Label = 'Custom target'; Path = [System.IO.Path]::GetFullPath($TargetPath) })
} else {
    $selectedHarnesses = if ($Harness.Count -eq 0) { @(Select-Harnesses) } else {
        if ($Harness -contains 'all') { @($harnessDefinitions) } else { @($harnessDefinitions | Where-Object { $_.Key -in $Harness }) }
    }
    $targets = @($selectedHarnesses | Group-Object Path | ForEach-Object { $_.Group[0] })
}

if ($targets.Count -eq 0) { throw 'No installation target selected.' }

if ($DryRun) {
    Write-Host 'Dry run: selected installation targets' -ForegroundColor Cyan
    $targets | ForEach-Object { Write-Host ("  {0}: {1}" -f $_.Label, $_.Path) }
    return
}

$existingTargets = @($targets | Where-Object { Test-Path -LiteralPath $_.Path })
if ($existingTargets.Count -gt 0 -and -not $Force) {
    Write-Host 'Existing skill directories:' -ForegroundColor Yellow
    $existingTargets | ForEach-Object { Write-Host ("  - {0}" -f $_.Path) }
    throw 'Target already exists. Use -Force to back up and replace the existing installation(s).'
}

if ([string]::IsNullOrWhiteSpace($StudentName)) { $StudentName = Read-Host 'Student name' }
if ([string]::IsNullOrWhiteSpace($StudentID)) { $StudentID = Read-Host 'Student ID' }
if ([string]::IsNullOrWhiteSpace($Major)) { $Major = Read-Host 'Major (optional)' }
if ([string]::IsNullOrWhiteSpace($College)) { $College = Read-Host 'College (per-user cover field; optional)' }
if ([string]::IsNullOrWhiteSpace($WordmarkFile)) {
    $WordmarkFile = Read-Host 'University wordmark image path (optional; Enter keeps bundled university branding)'
}
if ([string]::IsNullOrWhiteSpace($SealFile)) {
    $SealFile = Read-Host 'University seal/logo image path (optional; Enter keeps bundled university branding)'
}
if ([string]::IsNullOrWhiteSpace($StudentName) -or [string]::IsNullOrWhiteSpace($StudentID)) {
    throw 'Student name and student ID are required.'
}

$wordmarkSource = $null
$sealSource = $null
if (-not [string]::IsNullOrWhiteSpace($WordmarkFile)) {
    if (-not (Test-Path -LiteralPath $WordmarkFile -PathType Leaf)) { throw "Image file not found: $WordmarkFile" }
    $wordmarkSource = [System.IO.Path]::GetFullPath($WordmarkFile)
}
if (-not [string]::IsNullOrWhiteSpace($SealFile)) {
    if (-not (Test-Path -LiteralPath $SealFile -PathType Leaf)) { throw "Image file not found: $SealFile" }
    $sealSource = [System.IO.Path]::GetFullPath($SealFile)
}

$exclude = @(
    '.git', '.github', '.gitattributes', '.gitignore',
    'build', 'reports', 'output', 'tmp', 'docs', 'AGENTS.md', 'CHANGELOG.md',
    'personal-profile.json', 'profile.example.json', 'install.ps1', 'install.sh',
    '__pycache__'
)

function Copy-PersonalAsset([string]$source, [string]$prefix, [string]$fallback, [string]$assetDir) {
    if ([string]::IsNullOrWhiteSpace($source)) { return $fallback }
    $extension = [System.IO.Path]::GetExtension($source)
    if ([string]::IsNullOrWhiteSpace($extension)) { throw "Image has no file extension: $source" }
    $filename = "$prefix$extension"
    Copy-Item -LiteralPath $source -Destination (Join-Path $assetDir $filename) -Force
    return "assets/latex/lab-report/assets/$filename"
}

foreach ($targetDefinition in $targets) {
    $target = [System.IO.Path]::GetFullPath($targetDefinition.Path)
    if (Test-Path -LiteralPath $target) {
        $backup = "$target.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Move-Item -LiteralPath $target -Destination $backup
        Write-Host "Existing skill backed up to: $backup" -ForegroundColor Yellow
    }

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
    Get-ChildItem -LiteralPath $target -Directory -Recurse -Force |
        Where-Object { $_.Name -eq '__pycache__' } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -LiteralPath $target -File -Recurse -Force -Filter '*.pyc' |
        Remove-Item -Force -ErrorAction SilentlyContinue

    $assetDir = Join-Path $target 'assets\latex\lab-report\assets'
    New-Item -ItemType Directory -Force -Path $assetDir | Out-Null
    $wordmarkRelative = Copy-PersonalAsset $wordmarkSource 'custom-wordmark' 'assets/latex/lab-report/assets/university_wordmark.png' $assetDir
    $sealRelative = Copy-PersonalAsset $sealSource 'custom-seal' 'assets/latex/lab-report/assets/university_logo.jpeg' $assetDir

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
}

Write-Host ''
Write-Host 'Installed skill name: lab-report'
Write-Host 'Open your selected harness and ask it to use lab-report, or use its native skill command if available.'
Write-Host 'Personal details are stored only in each target skill directory under personal-profile.json.'
