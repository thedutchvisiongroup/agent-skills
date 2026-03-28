$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$SourceDir = Join-Path $RepoRoot "skills"
$TargetDir = Join-Path $env:USERPROFILE ".codeium\windsurf\skills"

Write-Host "Windsurf Skills Installer"
Write-Host "  Source: $SourceDir"
Write-Host "  Target: $TargetDir"
Write-Host ""

# Verify source directory exists
if (-not (Test-Path $SourceDir)) {
    Write-Error "Source directory not found: $SourceDir"
    exit 1
}

# Create parent directory if it does not exist
$ParentDir = Split-Path -Parent $TargetDir
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    Write-Host "Created parent directory: $ParentDir"
}

# Clear existing target directory if present
if (Test-Path $TargetDir) {
    Write-Host "Removing existing directory at $TargetDir"
    Remove-Item $TargetDir -Recurse -Force
}

# Copy skills to target directory
Copy-Item -Path $SourceDir -Destination $TargetDir -Recurse -Force
Write-Host "Done. Skills copied to $TargetDir"
