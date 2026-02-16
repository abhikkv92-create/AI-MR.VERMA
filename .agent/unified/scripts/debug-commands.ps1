# Debug the commands components structure
$commandsPath = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\commands\automation"
Write-Host "Checking commands component structure for: $commandsPath"

# List all files
Get-ChildItem -Path $commandsPath -Recurse | ForEach-Object {
    Write-Host "  $($_.FullName)" -ForegroundColor Yellow
}

# Check what files the QA framework expects
Write-Host "`nChecking required files:"
$requiredFiles = @("command.json", "implementation.js")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $commandsPath $file
    if (Test-Path $filePath) {
        Write-Host "  [PASS] $file exists" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $file missing" -ForegroundColor Red
    }
}