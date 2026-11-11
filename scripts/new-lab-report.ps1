[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$Course,
    [Parameter(Mandatory)] [string]$LabNumber,
    [Parameter(Mandatory)] [string]$Title,
    [string]$Student = '',
    [string]$StudentID = '',
    [string]$Major = '',
    [string]$College = '',
    [string]$WordmarkFile = '',
    [string]$SealFile = '',
    [string]$Date = '',
    [string]$CourseShort = '',
    [string]$ReportType = 'Experimental Report',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$DirectoryName = ''
)

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $PSScriptRoot
$templateRoot = Join-Path $skillRoot 'assets\latex\lab-report'
$profilePath = Join-Path $skillRoot 'personal-profile.json'
$projectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if (-not (Test-Path -LiteralPath $templateRoot -PathType Container)) {
    throw "User-level LaTeX template assets not found: $templateRoot"
}
if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    throw "Project root not found: $projectRoot"
}

$profile = $null
if (Test-Path -LiteralPath $profilePath -PathType Leaf) {
    $profile = Get-Content -LiteralPath $profilePath -Raw -Encoding utf8 | ConvertFrom-Json
}
if ([string]::IsNullOrWhiteSpace($Student) -and $profile) { $Student = [string]$profile.student_name }
if ([string]::IsNullOrWhiteSpace($StudentID) -and $profile) { $StudentID = [string]$profile.student_id }
if ([string]::IsNullOrWhiteSpace($Major) -and $profile) { $Major = [string]$profile.major }
if ([string]::IsNullOrWhiteSpace($College) -and $profile) { $College = [string]$profile.college }
if ([string]::IsNullOrWhiteSpace($Student) -or [string]::IsNullOrWhiteSpace($StudentID)) {
    throw "Student name and ID are missing. Run '.\install.ps1' from the shared repository or pass -Student and -StudentID."
}
if ([string]::IsNullOrWhiteSpace($CourseShort)) { $CourseShort = $Course }
if ([string]::IsNullOrWhiteSpace($Date)) {
    $Date = (Get-Date).ToString('d MMMM yyyy', [System.Globalization.CultureInfo]::InvariantCulture)
}

function ConvertTo-TeXText([string]$value) {
    if ($null -eq $value) { return '' }
    $s = $value.Replace('\', [char]1)
    $s = $s.Replace('&', '\&').Replace('%', '\%').Replace('#', '\#').Replace('_', '\_').Replace('$', '\$').Replace('{', '\{').Replace('}', '\}').Replace('~', '\textasciitilde{}').Replace('^', '\textasciicircum{}')
    return $s.Replace([string][char]1, '\textbackslash{}')
}

function Resolve-ProfilePath([string]$value, [string]$fallback) {
    if ([string]::IsNullOrWhiteSpace($value)) { return $fallback }
    if ([System.IO.Path]::IsPathRooted($value)) { return $value }
    return Join-Path $skillRoot $value
}

if ([string]::IsNullOrWhiteSpace($WordmarkFile) -and $profile) { $WordmarkFile = [string]$profile.wordmark_file }
if ([string]::IsNullOrWhiteSpace($SealFile) -and $profile) { $SealFile = [string]$profile.seal_file }
$WordmarkFile = Resolve-ProfilePath $WordmarkFile (Join-Path $templateRoot 'assets\university_wordmark.png')
$SealFile = Resolve-ProfilePath $SealFile (Join-Path $templateRoot 'assets\university_logo.jpeg')
if (-not (Test-Path -LiteralPath $WordmarkFile -PathType Leaf)) { throw "Wordmark image not found: $WordmarkFile" }
if (-not (Test-Path -LiteralPath $SealFile -PathType Leaf)) { throw "Seal image not found: $SealFile" }
$WordmarkFile = [System.IO.Path]::GetFullPath($WordmarkFile)
$SealFile = [System.IO.Path]::GetFullPath($SealFile)

$courseSlug = ($Course -replace '[^\p{L}\p{Nd}]+', '_').Trim('_')
if ([string]::IsNullOrWhiteSpace($DirectoryName)) { $DirectoryName = "Lab${LabNumber}_${courseSlug}" }
$reportRoot = Join-Path $projectRoot 'reports'
$reportDir = Join-Path $reportRoot $DirectoryName
if (Test-Path -LiteralPath $reportDir) { throw "Report directory already exists: $reportDir" }

New-Item -ItemType Directory -Force -Path $reportRoot, $reportDir, (Join-Path $reportDir 'figures'), (Join-Path $reportDir 'build') | Out-Null

$templateMain = Get-Content -LiteralPath (Join-Path $templateRoot 'main-template.tex') -Raw -Encoding utf8
$main = $templateMain
$wordmarkPath = $WordmarkFile.Replace('\','/')
$sealPath = $SealFile.Replace('\','/')
$main = $main.Replace('\LabWordmarkFile{assets/university_wordmark.png}', "\LabWordmarkFile{$wordmarkPath}")
$main = $main.Replace('\LabSealFile{assets/university_logo.jpeg}', "\LabSealFile{$sealPath}")
$replacements = [ordered]@{
    '@@COURSE@@' = ConvertTo-TeXText $Course
    '@@COURSESHORT@@' = ConvertTo-TeXText $CourseShort
    '@@REPORTTYPE@@' = ConvertTo-TeXText $ReportType
    '@@LABNUMBER@@' = ConvertTo-TeXText $LabNumber
    '@@TITLE@@' = ConvertTo-TeXText $Title
    '@@STUDENT@@' = ConvertTo-TeXText $Student
    '@@STUDENTID@@' = ConvertTo-TeXText $StudentID
    '@@MAJOR@@' = ConvertTo-TeXText $Major
    '@@COLLEGE@@' = ConvertTo-TeXText $College
    '@@DATE@@' = ConvertTo-TeXText $Date
    '@@HEADERLEFT@@' = ConvertTo-TeXText $CourseShort
    '@@HEADERRIGHT@@' = ConvertTo-TeXText ("Laboratory $LabNumber")
}
foreach ($entry in $replacements.GetEnumerator()) { $main = $main.Replace($entry.Key, $entry.Value) }
Set-Content -LiteralPath (Join-Path $reportDir 'main.tex') -Value $main -Encoding utf8

$compilerScript = Join-Path $skillRoot 'scripts\compile-report.ps1'
$wrapperLines = @(
    '[CmdletBinding()]',
    'param(',
    '    [switch]$AllowPending,',
    "    [string]`$OutputPdf = ''",
    ')',
    '',
    "& '$($compilerScript.Replace("'", "''"))' -ReportDir `$PSScriptRoot -TemplateRoot '$($templateRoot.Replace("'", "''"))' -OutputPdf `$OutputPdf -AllowPending:`$AllowPending",
    'exit $LASTEXITCODE'
)
Set-Content -LiteralPath (Join-Path $reportDir 'compile-report.ps1') -Value ($wrapperLines -join "`n") -Encoding utf8

$config = [ordered]@{
    course = $Course
    course_short = $CourseShort
    report_type = $ReportType
    lab_number = $LabNumber
    title = $Title
    student = $Student
    student_id = $StudentID
    major = $Major
    college = $College
    date = $Date
    template_root = $templateRoot
    wordmark_file = $WordmarkFile
    seal_file = $SealFile
    created_at = (Get-Date).ToString('o')
}
$config | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $reportDir 'report.config.json') -Encoding utf8

Set-Content -LiteralPath (Join-Path $reportDir 'README.md') -Encoding utf8 -Value @"
# $Course - Laboratory $LabNumber

$Title

The LaTeX style and cover assets are loaded from the user-level `lab-report` skill. This report does not copy a shared project template.

## Structure

- `main.tex`: report source and body outline
- `figures/`: optional data charts and user-supplied images
- `build/`: generated LaTeX files and page renders

## Build

```powershell
.\compile-report.ps1 -AllowPending
.\compile-report.ps1
```

Final mode rejects `[PENDING:` markers and missing images referenced through `LabFigure`.
"@

Write-Host "Report scaffold: $reportDir" -ForegroundColor Green
Write-Host "Template source: $templateRoot"
Write-Host "Personal profile: $profilePath"
Write-Host "Next: edit main.tex, add optional figures, then run .\compile-report.ps1 -AllowPending"
