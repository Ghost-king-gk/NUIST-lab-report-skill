[CmdletBinding()]
param(
    [string]$ReportDir = (Get-Location).Path,
    [string]$MainFile = 'main.tex',
    [string]$OutputPdf = '',
    [string]$TemplateRoot = '',
    [switch]$AllowPending
)

$ErrorActionPreference = 'Stop'
$reportRoot = [System.IO.Path]::GetFullPath($ReportDir)
$mainPath = Join-Path $reportRoot $MainFile

if (-not (Test-Path -LiteralPath $mainPath -PathType Leaf)) {
    throw "Main TeX file not found: $mainPath"
}
foreach ($command in @('latexmk', 'pdftoppm', 'pdfinfo')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $command"
    }
}

if ([string]::IsNullOrWhiteSpace($TemplateRoot)) {
    $TemplateRoot = $env:LAB_REPORT_TEMPLATE
}
if ([string]::IsNullOrWhiteSpace($TemplateRoot)) {
    $candidate = Join-Path (Split-Path $PSScriptRoot -Parent) 'assets\latex\lab-report'
    if (Test-Path -LiteralPath $candidate -PathType Container) {
        $TemplateRoot = $candidate
    }
}
if ([string]::IsNullOrWhiteSpace($TemplateRoot) -or -not (Test-Path -LiteralPath $TemplateRoot -PathType Container)) {
    throw "Lab report template root not found. Pass -TemplateRoot or set LAB_REPORT_TEMPLATE."
}
$TemplateRoot = [System.IO.Path]::GetFullPath($TemplateRoot)

$pending = Select-String -LiteralPath $mainPath -Pattern '\[PENDING:|\\LabPending\{' -ErrorAction Stop
if (-not $AllowPending -and $pending) {
    Write-Host 'Report still contains PENDING markers:' -ForegroundColor Yellow
    $pending | ForEach-Object { Write-Host ("  line {0}: {1}" -f $_.LineNumber, $_.Line.Trim()) }
    exit 1
}

$evidenceMatches = Select-String -LiteralPath $mainPath -Pattern '\\LabEvidenceFigure(?:\[[^\]]*\])?\{([^}]+)\}' -AllMatches
if ($evidenceMatches) {
    $missing = @()
    foreach ($match in $evidenceMatches.Matches) {
        $relative = $match.Groups[1].Value
        $path = Join-Path $reportRoot (Join-Path 'figures' $relative)
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $missing += "figures/$relative"
        }
    }
    if ($missing.Count -gt 0) {
        Write-Host 'Missing report figures:' -ForegroundColor Yellow
        $missing | Sort-Object -Unique | ForEach-Object { Write-Host "  - $_" }
        exit 1
    }
}

$oldTexInputs = $env:TEXINPUTS
$env:TEXINPUTS = "$TemplateRoot;$($env:TEXINPUTS)"
Push-Location $reportRoot
try {
    & latexmk -pdf -interaction=nonstopmode -halt-on-error (Split-Path $mainPath -Leaf)
    if ($LASTEXITCODE -ne 0) {
        throw "latexmk failed with exit code $LASTEXITCODE"
    }

    $pdfPath = [System.IO.Path]::ChangeExtension($mainPath, '.pdf')
    $logPath = [System.IO.Path]::ChangeExtension($mainPath, '.log')
    if (-not (Test-Path -LiteralPath $pdfPath -PathType Leaf)) {
        throw "PDF was not produced: $pdfPath"
    }

    $layoutWarnings = Select-String -LiteralPath $logPath -Pattern 'Overfull|Underfull' -ErrorAction SilentlyContinue
    if ($layoutWarnings) {
        Write-Host 'Layout warnings found:' -ForegroundColor Yellow
        $layoutWarnings | ForEach-Object { Write-Host ("  line {0}: {1}" -f $_.LineNumber, $_.Line.Trim()) }
        exit 1
    }

    $pagesDir = Join-Path $reportRoot 'build\pages'
    New-Item -ItemType Directory -Force -Path $pagesDir | Out-Null
    & pdftoppm -png -r 120 $pdfPath (Join-Path $pagesDir 'page')
    if ($LASTEXITCODE -ne 0) {
        throw "pdftoppm failed with exit code $LASTEXITCODE"
    }

    $pageLine = & pdfinfo $pdfPath | Select-String -Pattern '^Pages:' | Select-Object -First 1
    $pageCount = 'unknown'
    if ($pageLine -and $pageLine.Line -match 'Pages:\s+(\d+)') {
        $pageCount = $Matches[1]
    }

    if ($OutputPdf) {
        $destination = [System.IO.Path]::GetFullPath($OutputPdf)
        Copy-Item -LiteralPath $pdfPath -Destination $destination -Force
        Write-Host "Output PDF: $destination" -ForegroundColor Green
    } else {
        Write-Host "Output PDF: $pdfPath" -ForegroundColor Green
    }
    Write-Host "Pages: $pageCount"
    Write-Host "Page renders: $pagesDir"
}
finally {
    Pop-Location
    if ($null -eq $oldTexInputs) {
        Remove-Item Env:TEXINPUTS -ErrorAction SilentlyContinue
    } else {
        $env:TEXINPUTS = $oldTexInputs
    }
}
