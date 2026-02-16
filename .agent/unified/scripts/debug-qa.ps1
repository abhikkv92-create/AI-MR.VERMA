# Test script to debug QA issues
$settingsPath = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\settings\statusline\command-statusline"
Write-Host "Testing settings component: $settingsPath"

# Check required files
$requiredFiles = @("setting.json", "implementation.js")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $settingsPath $file
    Write-Host "Checking $filePath..."
    if (Test-Path $filePath) {
        Write-Host "  [PASS] $file exists" -ForegroundColor Green
        
        # Check content
        $content = Get-Content $filePath -Raw
        if ($file -eq "implementation.js") {
            $hasClass = $content -match "class\s+\w+"
            $hasModule = $content -match "module\.exports"
            Write-Host "  Has class: $hasClass" -ForegroundColor Yellow
            Write-Host "  Has module.exports: $hasModule" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] $file missing" -ForegroundColor Red
    }
}

# Check JSON validity
$jsonFile = Join-Path $settingsPath "setting.json"
if (Test-Path $jsonFile) {
    try {
        $json = Get-Content $jsonFile -Raw | ConvertFrom-Json
        Write-Host "  [PASS] JSON is valid" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] JSON is invalid: $($_.Exception.Message)" -ForegroundColor Red
    }
}