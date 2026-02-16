# Fix the directory structure for settings and hooks components

# Fix settings components
$settingsComponents = @(
    "command-statusline",
    "game-performance-monitor-statusline", 
    "unity-project-dashboard-statusline",
    "vercel-multi-env-status"
)

foreach ($component in $settingsComponents) {
    $sourceDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\settings\statusline\$component"
    $targetDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\settings\$component"
    
    Write-Host "Moving $sourceDir to $targetDir" -ForegroundColor Yellow
    if (Test-Path $sourceDir) {
        Move-Item -Path $sourceDir -Destination $targetDir -Force
        Write-Host "  [SUCCESS] Moved $component" -ForegroundColor Green
    }
}

# Fix hooks components  
$hooksComponents = @(
    "development-tools",
    "performance",
    "post-tool", 
    "testing"
)

foreach ($component in $hooksComponents) {
    $sourceDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\hooks\$component"
    
    # Find the actual component subdirectory
    $subdirs = Get-ChildItem -Path $sourceDir -Directory
    foreach ($subdir in $subdirs) {
        $componentName = $subdir.Name
        $sourceSubDir = $subdir.FullName
        $targetDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\hooks\$componentName"
        
        Write-Host "Moving $sourceSubDir to $targetDir" -ForegroundColor Yellow
        if (Test-Path $sourceSubDir) {
            Move-Item -Path $sourceSubDir -Destination $targetDir -Force
            Write-Host "  [SUCCESS] Moved $componentName" -ForegroundColor Green
        }
    }
}

Write-Host "Directory structure fix completed!" -ForegroundColor Green