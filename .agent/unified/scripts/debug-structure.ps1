# Debug the actual directory structure
$settingsPath = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\settings\statusline"
Write-Host "Directory structure for $settingsPath"

# List all files recursively
Get-ChildItem -Path $settingsPath -Recurse | ForEach-Object {
    Write-Host "  $($_.FullName)" -ForegroundColor Yellow
}

Write-Host "`nChecking what the QA framework sees:"
$requiredFiles = @("setting.json", "implementation.js")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $settingsPath $file
    Write-Host "Looking for: $filePath"
    if (Test-Path $filePath) {
        Write-Host "  [PASS] Found directly in component directory" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Not found directly in component directory" -ForegroundColor Red
    }
}