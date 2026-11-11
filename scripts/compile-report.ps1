[CmdletBinding()]
param(
    [string]$ReportDir = (Get-Location).Path,
    [ValidateSet('docx', 'pdf', 'both')]
    [string[]]$Formats = @('docx', 'pdf'),
    [ValidateSet('auto', 'office', 'latex')]
    [string]$PdfBackend = 'auto',
    [string]$Python = 'python',
    [switch]$AllowPending
)

$ErrorActionPreference = 'Stop'
$tool = Join-Path $PSScriptRoot 'report_tool.py'
if (-not (Test-Path -LiteralPath $tool -PathType Leaf)) {
    throw "Report tool not found: $tool"
}
$pythonCommand = Get-Command $Python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python executable not found: $Python"
}

$arguments = @(
    $tool,
    'build',
    '--report-dir', $ReportDir,
    '--formats', ($Formats -join ','),
    '--pdf-backend', $PdfBackend
)
if ($AllowPending) { $arguments += '--allow-pending' }

& $pythonCommand.Source @arguments
exit $LASTEXITCODE
