[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$Course,
    [Parameter(Mandatory)] [string]$LabNumber,
    [Parameter(Mandatory)] [string]$Title,
    [string]$Student = '',
    [string]$StudentID = '',
    [string]$Major = '',
    [string]$College = '',
    [string]$CourseShort = '',
    [string]$ReportType = 'Experimental Report',
    [string]$Date = '',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$DirectoryName = '',
    [string]$Python = 'python',
    [ValidateSet('docx', 'pdf', 'both')]
    [string]$Format = 'docx'
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
    'new',
    '--project-root', $ProjectRoot,
    '--course', $Course,
    '--lab-number', $LabNumber,
    '--title', $Title,
    '--report-type', $ReportType,
    '--format', $Format
)
foreach ($entry in @(
    @('--student', $Student),
    @('--student-id', $StudentID),
    @('--major', $Major),
    @('--college', $College),
    @('--course-short', $CourseShort),
    @('--date', $Date),
    @('--directory-name', $DirectoryName)
)) {
    if (-not [string]::IsNullOrWhiteSpace([string]$entry[1])) {
        $arguments += $entry
    }
}

& $pythonCommand.Source @arguments
exit $LASTEXITCODE
