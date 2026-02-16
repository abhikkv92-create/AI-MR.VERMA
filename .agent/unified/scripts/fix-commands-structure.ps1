# Fix the commands component structure
$commandsComponents = @(
    "automation",
    "deployment", 
    "performance",
    "team"
)

foreach ($component in $commandsComponents) {
    $sourceDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\commands\$component"
    
    # Find the actual component subdirectory
    $subdirs = Get-ChildItem -Path $sourceDir -Directory
    foreach ($subdir in $subdirs) {
        $componentName = $subdir.Name
        $sourceSubDir = $subdir.FullName
        $targetDir = "e:\ABHINAV\MR.VERMA\.agent\unified\templates\commands\$componentName"
        
        Write-Host "Moving $sourceSubDir to $targetDir" -ForegroundColor Yellow
        if (Test-Path $sourceSubDir) {
            Move-Item -Path $sourceSubDir -Destination $targetDir -Force
            Write-Host "  [SUCCESS] Moved $componentName" -ForegroundColor Green
        }
    }
}

Write-Host "Commands structure fix completed!" -ForegroundColor Green