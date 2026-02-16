# Redundancy Elimination and Optimization Engine
# Comprehensive duplicate detection, analysis, and removal system

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$UNIFIED_DIR = "$PROJECT_ROOT\.agent\unified"
$OPTIMIZATION_DIR = "$UNIFIED_DIR\optimization"
$REDUNDANCY_LOG = "$OPTIMIZATION_DIR\redundancy-elimination.log"
$DUPLICATE_DATABASE = "$OPTIMIZATION_DIR\duplicate-database.json"
$OPTIMIZATION_REPORT = "$OPTIMIZATION_DIR\optimization-report.json"

# Optimization statistics
$optimizationStats = @{
    scanStartTime = $null
    scanEndTime = $null
    totalFiles = 0
    duplicateGroups = 0
    duplicatesFound = 0
    spaceSaved = 0
    filesRemoved = 0
    directoriesCleaned = 0
    optimizationLevel = "comprehensive"
}

function Write-OptimizationLog {
    param(
        [string]$Message,
        [string]$Type = "INFO",
        [switch]$ConsoleOnly
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Type] $Message"
    
    # Console output
    switch ($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "DUPLICATE" { Write-Host $logEntry -ForegroundColor Magenta }
        "OPTIMIZATION" { Write-Host $logEntry -ForegroundColor Cyan }
        default { Write-Host $logEntry -ForegroundColor White }
    }
    
    # File logging
    if (-not $ConsoleOnly) {
        Add-Content -Path $REDUNDANCY_LOG -Value $logEntry -ErrorAction SilentlyContinue
    }
}

function Initialize-OptimizationEnvironment {
    Write-OptimizationLog "Initializing Redundancy Elimination Environment..." "OPTIMIZATION"
    
    # Create optimization directories
    @($OPTIMIZATION_DIR, "$OPTIMIZATION_DIR\backups", "$OPTIMIZATION_DIR\analysis") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-OptimizationLog "Created optimization directory: $_" "SUCCESS"
        }
    }
    
    # Initialize log file
    "Redundancy Elimination Log - $(Get-Date)" | Out-File -FilePath $REDUNDANCY_LOG -Force
    Write-OptimizationLog "Optimization environment initialized successfully" "SUCCESS"
}

function Get-AdvancedFileChecksum {
    param(
        [string]$FilePath,
        [string]$Algorithm = "SHA256"
    )
    
    try {
        if (Test-Path $FilePath) {
            $fileInfo = Get-Item $FilePath
            
            # For small files, use full content hash
            if ($fileInfo.Length -lt 1MB) {
                $content = [System.IO.File]::ReadAllBytes($FilePath)
                $hasher = [System.Security.Cryptography.SHA256]::Create()
                $hashBytes = $hasher.ComputeHash($content)
                $hasher.Dispose()
                
                return [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()
            }
            else {
                # For large files, use sampling approach
                $stream = [System.IO.File]::OpenRead($FilePath)
                $hasher = [System.Security.Cryptography.SHA256]::Create()
                
                # Read first 1KB, middle 1KB, and last 1KB
                $buffer = New-Object byte[] 1024
                
                # First 1KB
                $bytesRead = $stream.Read($buffer, 0, 1024)
                if ($bytesRead -gt 0) {
                    $hasher.TransformBlock($buffer, 0, $bytesRead, $buffer, 0) | Out-Null
                }
                
                # Middle 1KB
                $middlePosition = [math]::Max(0, ($stream.Length / 2) - 512)
                $stream.Position = $middlePosition
                $bytesRead = $stream.Read($buffer, 0, 1024)
                if ($bytesRead -gt 0) {
                    $hasher.TransformBlock($buffer, 0, $bytesRead, $buffer, 0) | Out-Null
                }
                
                # Last 1KB
                $stream.Position = [math]::Max(0, $stream.Length - 1024)
                $bytesRead = $stream.Read($buffer, 0, 1024)
                if ($bytesRead -gt 0) {
                    $hasher.TransformBlock($buffer, 0, $bytesRead, $buffer, 0) | Out-Null
                }
                
                $hasher.TransformFinalBlock($buffer, 0, 0) | Out-Null
                $hashBytes = $hasher.Hash
                $stream.Close()
                $hasher.Dispose()
                
                return [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()
            }
        }
    }
    catch {
        Write-OptimizationLog "Error calculating checksum for $FilePath: $($_.Exception.Message)" "WARNING"
        return $null
    }
    
    return $null
}

function Analyze-FileSimilarity {
    param(
        [string]$File1,
        [string]$File2
    )
    
    try {
        $content1 = Get-Content $File1 -Raw -ErrorAction SilentlyContinue
        $content2 = Get-Content $File2 -Raw -ErrorAction SilentlyContinue
        
        if ($content1 -and $content2) {
            # Calculate similarity ratio
            $len1 = $content1.Length
            $len2 = $content2.Length
            
            # Simple similarity check (can be enhanced with more sophisticated algorithms)
            $commonLines = 0
            $lines1 = $content1 -split "`n"
            $lines2 = $content2 -split "`n"
            
            foreach ($line1 in $lines1) {
                if ($line1.Trim() -and $lines2 -contains $line1.Trim()) {
                    $commonLines++
                }
            }
            
            $similarity = [math]::Round(($commonLines / [math]::Max($lines1.Count, $lines2.Count)) * 100, 2)
            
            return @{
                similarity = $similarity
                commonLines = $commonLines
                totalLines1 = $lines1.Count
                totalLines2 = $lines2.Count
                isDuplicate = $similarity -gt 90
            }
        }
    }
    catch {
        Write-OptimizationLog "Error analyzing similarity: $($_.Exception.Message)" "WARNING"
    }
    
    return @{ similarity = 0; isDuplicate = $false }
}

function Scan-ComprehensiveDuplicates {
    param(
        [string]$ScanPath = "$UNIFIED_DIR\templates",
        [switch]$DeepScan
    )
    
    Write-OptimizationLog "Starting comprehensive duplicate scan..." "OPTIMIZATION"
    $optimizationStats.scanStartTime = Get-Date
    
    $duplicateDatabase = @{
        scanTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        scanPath = $ScanPath
        duplicateGroups = @{}
        fileRegistry = @{}
        optimizationOpportunities = @()
    }
    
    if (-not (Test-Path $ScanPath)) {
        Write-OptimizationLog "Scan path does not exist: $ScanPath" "ERROR"
        return $duplicateDatabase
    }
    
    # Get all files recursively
    $allFiles = Get-ChildItem -Path $ScanPath -File -Recurse -ErrorAction SilentlyContinue
    $optimizationStats.totalFiles = $allFiles.Count
    
    Write-OptimizationLog "Found $($allFiles.Count) files to analyze" "INFO"
    
    $progress = 0
    $fileHashes = @{}
    
    foreach ($file in $allFiles) {
        $progress++
        if ($progress % 100 -eq 0) {
            Write-OptimizationLog "Progress: $progress/$($allFiles.Count) files analyzed" "INFO" -ConsoleOnly
        }
        
        # Calculate checksum
        $checksum = Get-AdvancedFileChecksum -FilePath $file.FullName
        
        if ($checksum) {
            # Register file in registry
            $fileInfo = @{
                path = $file.FullName
                name = $file.Name
                size = $file.Length
                lastModified = $file.LastWriteTime
                checksum = $checksum
                relativePath = $file.FullName.Substring($ScanPath.Length + 1)
            }
            
            $duplicateDatabase.fileRegistry[$file.FullName] = $fileInfo
            
            # Check for duplicates
            if ($fileHashes.ContainsKey($checksum)) {
                # Found duplicate group
                if (-not $duplicateDatabase.duplicateGroups.ContainsKey($checksum)) {
                    $duplicateDatabase.duplicateGroups[$checksum] = @{
                        original = $fileHashes[$checksum]
                        duplicates = @()
                        totalSize = $fileHashes[$checksum].size
                        checksum = $checksum
                    }
                }
                
                $duplicateDatabase.duplicateGroups[$checksum].duplicates += $fileInfo
                $duplicateDatabase.duplicateGroups[$checksum].totalSize += $file.Size
                
                Write-OptimizationLog "Found duplicate: $($file.Name) matches $($fileHashes[$checksum].name)" "DUPLICATE"
            }
            else {
                $fileHashes[$checksum] = $fileInfo
            }
            
            # Deep scan for similar files (not just exact duplicates)
            if ($DeepScan -and $file.Extension -in @(".js", ".py", ".json", ".md")) {
                foreach ($existingFile in $fileHashes.Values) {
                    if ($existingFile.path -ne $file.FullName -and $existingFile.extension -eq $file.Extension) {
                        $similarity = Analyze-FileSimilarity -File1 $file.FullName -File2 $existingFile.path
                        
                        if ($similarity.isDuplicate -and $similarity.similarity -lt 100) {
                            Write-OptimizationLog "Found similar file: $($file.Name) ~ $($existingFile.name) ($($similarity.similarity)% similarity)" "DUPLICATE"
                            
                            $duplicateDatabase.optimizationOpportunities += @{
                                type = "similar"
                                file1 = $file.FullName
                                file2 = $existingFile.path
                                similarity = $similarity.similarity
                                recommendation = "Consider consolidating similar files"
                            }
                        }
                    }
                }
            }
        }
    }
    
    $optimizationStats.scanEndTime = Get-Date
    $optimizationStats.duplicateGroups = $duplicateDatabase.duplicateGroups.Count
    $optimizationStats.duplicatesFound = ($duplicateDatabase.duplicateGroups.Values | Measure-Object -Property duplicates -Sum).Sum
    
    Write-OptimizationLog "Duplicate scan completed. Found $($optimizationStats.duplicateGroups) duplicate groups with $($optimizationStats.duplicatesFound) duplicates" "SUCCESS"
    
    # Save duplicate database
    $duplicateDatabase | ConvertTo-Json -Depth 4 | Out-File -FilePath $DUPLICATE_DATABASE -Encoding UTF8
    Write-OptimizationLog "Duplicate database saved to: $DUPLICATE_DATABASE" "SUCCESS"
    
    return $duplicateDatabase
}

function Calculate-OptimizationPotential {
    param([hashtable]$DuplicateDatabase)
    
    Write-OptimizationLog "Calculating optimization potential..." "OPTIMIZATION"
    
    $optimizationAnalysis = @{
        totalSpaceWasted = 0
        filesThatCanBeRemoved = 0
        directoriesThatCanBeCleaned = 0
        optimizationStrategies = @()
        recommendations = @()
    }
    
    foreach ($duplicateGroup in $DuplicateDatabase.duplicateGroups.Values) {
        $duplicatesCount = $duplicateGroup.duplicates.Count
        $spaceWasted = $duplicateGroup.totalSize - $duplicateGroup.original.size
        
        $optimizationAnalysis.totalSpaceWasted += $spaceWasted
        $optimizationAnalysis.filesThatCanBeRemoved += $duplicatesCount
        
        # Calculate potential space savings
        $optimizationStrategies += @{
            checksum = $duplicateGroup.checksum
            originalFile = $duplicateGroup.original.path
            duplicateCount = $duplicatesCount
            spaceWasted = $spaceWasted
            recommendedAction = "Remove $duplicatesCount duplicates, keep original"
            priority = if ($spaceWasted -gt 1MB) { "high" } elseif ($spaceWasted -gt 100KB) { "medium" } else { "low" }
        }
    }
    
    $optimizationStats.spaceSaved = $optimizationAnalysis.totalSpaceWasted
    
    # Generate recommendations
    if ($optimizationAnalysis.totalSpaceWasted -gt 10MB) {
        $optimizationAnalysis.recommendations += "High-impact optimization: Can save $([math]::Round($optimizationAnalysis.totalSpaceWasted / 1MB, 2)) MB"
    }
    
    if ($optimizationAnalysis.filesThatCanBeRemoved -gt 50) {
        $optimizationAnalysis.recommendations += "Large-scale cleanup: Can remove $($optimizationAnalysis.filesThatCanBeRemoved) duplicate files"
    }
    
    if ($DuplicateDatabase.optimizationOpportunities.Count -gt 0) {
        $optimizationAnalysis.recommendations += "Similarity optimization: Found $($DuplicateDatabase.optimizationOpportunities.Count) similar files that could be consolidated"
    }
    
    Write-OptimizationLog "Optimization analysis completed. Potential space savings: $([math]::Round($optimizationAnalysis.totalSpaceWasted / 1MB, 2)) MB" "SUCCESS"
    
    return $optimizationAnalysis
}

function Execute-RedundancyElimination {
    param(
        [hashtable]$DuplicateDatabase,
        [switch]$WhatIf = $true,
        [switch]$BackupFirst = $true
    )
    
    Write-OptimizationLog "Executing redundancy elimination (WhatIf: $WhatIf)..." "OPTIMIZATION"
    
    $eliminationResults = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        whatIfMode = $WhatIf
        filesRemoved = @()
        spaceReclaimed = 0
        errors = @()
        backupLocation = $null
    }
    
    if ($BackupFirst -and -not $WhatIf) {
        Write-OptimizationLog "Creating backup before elimination..." "OPTIMIZATION"
        $backupPath = "$OPTIMIZATION_DIR\backups\pre-elimination-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        
        try {
            # Create backup of affected directories
            $affectedDirectories = $DuplicateDatabase.duplicateGroups.Values | 
                ForEach-Object { $_.original.path } | 
                ForEach-Object { Split-Path $_ -Parent } | 
                Select-Object -Unique
            
            foreach ($dir in $affectedDirectories) {
                $backupDir = $backupPath + $dir.Substring($UNIFIED_DIR.Length)
                if (Test-Path $dir) {
                    Copy-Item -Path $dir -Destination $backupDir -Recurse -Force
                }
            }
            
            $eliminationResults.backupLocation = $backupPath
            Write-OptimizationLog "Backup created at: $backupPath" "SUCCESS"
        }
        catch {
            Write-OptimizationLog "Backup creation failed: $($_.Exception.Message)" "ERROR"
            $eliminationResults.errors += "Backup failed: $($_.Exception.Message)"
        }
    }
    
    # Process duplicate groups
    foreach ($duplicateGroup in $DuplicateDatabase.duplicateGroups.Values) {
        Write-OptimizationLog "Processing duplicate group: $($duplicateGroup.checksum)" "INFO"
        
        foreach ($duplicate in $duplicateGroup.duplicates) {
            try {
                if (Test-Path $duplicate.path) {
                    $fileInfo = Get-Item $duplicate.path
                    $spaceReclaimed = $fileInfo.Length
                    
                    if (-not $WhatIf) {
                        Remove-Item -Path $duplicate.path -Force
                        Write-OptimizationLog "Removed duplicate: $($duplicate.path)" "DUPLICATE"
                    }
                    else {
                        Write-OptimizationLog "[WHATIF] Would remove: $($duplicate.path)" "DUPLICATE"
                    }
                    
                    $eliminationResults.filesRemoved += @{
                        path = $duplicate.path
                        size = $spaceReclaimed
                        original = $duplicateGroup.original.path
                        removed = -not $WhatIf
                    }
                    
                    $eliminationResults.spaceReclaimed += $spaceReclaimed
                    $optimizationStats.filesRemoved++
                }
            }
            catch {
                $errorMsg = "Failed to remove $($duplicate.path): $($_.Exception.Message)"
                Write-OptimizationLog $errorMsg "ERROR"
                $eliminationResults.errors += $errorMsg
            }
        }
    }
    
    # Clean up empty directories
    $cleanedDirs = Remove-EmptyDirectories -BasePath "$UNIFIED_DIR\templates"
    $eliminationResults.directoriesCleaned = $cleanedDirs
    $optimizationStats.directoriesCleaned = $cleanedDirs.Count
    
    Write-OptimizationLog "Redundancy elimination completed. Space reclaimed: $([math]::Round($eliminationResults.spaceReclaimed / 1MB, 2)) MB" "SUCCESS"
    
    return $eliminationResults
}

function Remove-EmptyDirectories {
    param([string]$BasePath)
    
    $removedDirs = @()
    
    Get-ChildItem -Path $BasePath -Directory -Recurse | Sort-Object FullName -Descending | ForEach-Object {
        $dir = $_
        $files = Get-ChildItem -Path $dir.FullName -File -Recurse
        $subDirs = Get-ChildItem -Path $dir.FullName -Directory
        
        if ($files.Count -eq 0 -and $subDirs.Count -eq 0) {
            try {
                Remove-Item -Path $dir.FullName -Force
                $removedDirs += $dir.FullName
                Write-OptimizationLog "Removed empty directory: $($dir.FullName)" "INFO"
            }
            catch {
                Write-OptimizationLog "Failed to remove empty directory $($dir.FullName): $($_.Exception.Message)" "WARNING"
            }
        }
    }
    
    return $removedDirs
}

function Generate-OptimizationReport {
    param([hashtable]$EliminationResults, [hashtable]$OptimizationAnalysis)
    
    Write-OptimizationLog "Generating optimization report..." "OPTIMIZATION"
    
    $finalReport = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        optimizationStats = $optimizationStats
        eliminationResults = $EliminationResults
        optimizationAnalysis = $OptimizationAnalysis
        recommendations = @(
            "Regular duplicate scans (weekly/monthly)",
            "Implement file size thresholds for automatic cleanup",
            "Establish naming conventions to prevent future duplicates",
            "Monitor template creation for duplicate patterns",
            "Consider implementing deduplication at creation time"
        )
        nextSteps = @(
            "Schedule automated optimization runs",
            "Create template validation pipeline",
            "Implement real-time duplicate detection",
            "Establish optimization metrics and KPIs"
        )
    }
    
    # Save final report
    $finalReport | ConvertTo-Json -Depth 5 | Out-File -FilePath $OPTIMIZATION_REPORT -Encoding UTF8
    Write-OptimizationLog "Optimization report saved to: $OPTIMIZATION_REPORT" "SUCCESS"
    
    return $finalReport
}

function Show-OptimizationDashboard {
    Write-Host "`n=== Redundancy Elimination Dashboard ===" -ForegroundColor Cyan
    Write-Host "Project: MR.VERMA Unified System" -ForegroundColor White
    Write-Host "Optimization Directory: $OPTIMIZATION_DIR" -ForegroundColor Gray
    Write-Host "Last Scan: $(if($optimizationStats.scanEndTime){$optimizationStats.scanEndTime.ToString('yyyy-MM-dd HH:mm:ss')}else{'Never'})" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📊 Optimization Statistics:" -ForegroundColor Yellow
    Write-Host "  Total Files Analyzed: $($optimizationStats.totalFiles)" -ForegroundColor White
    Write-Host "  Duplicate Groups Found: $($optimizationStats.duplicateGroups)" -ForegroundColor White
    Write-Host "  Duplicate Files: $($optimizationStats.duplicatesFound)" -ForegroundColor $(if($optimizationStats.duplicatesFound -gt 0){"Red"} else {"Green"})
    Write-Host "  Space Wasted: $([math]::Round($optimizationStats.spaceSaved / 1MB, 2)) MB" -ForegroundColor $(if($optimizationStats.spaceSaved -gt 1MB){"Red"} else {"Green"})
    Write-Host "  Files Removed: $($optimizationStats.filesRemoved)" -ForegroundColor $(if($optimizationStats.filesRemoved -gt 0){"Green"} else {"White"})
    Write-Host "  Directories Cleaned: $($optimizationStats.directoriesCleaned)" -ForegroundColor $(if($optimizationStats.directoriesCleaned -gt 0){"Green"} else {"White"})
    
    Write-Host "`n🔧 Available Actions:" -ForegroundColor Yellow
    Write-Host "  1. Scan for duplicates" -ForegroundColor White
    Write-Host "  2. Analyze optimization potential" -ForegroundColor White
    Write-Host "  3. Preview elimination (WhatIf)" -ForegroundColor White
    Write-Host "  4. Execute elimination" -ForegroundColor White
    Write-Host "  5. Generate optimization report" -ForegroundColor White
    Write-Host "  6. Clean empty directories" -ForegroundColor White
    
    Write-Host ""
}

function Main {
    param([string]$Action = "dashboard", [switch]$DeepScan, [switch]$WhatIf)
    
    try {
        Initialize-OptimizationEnvironment
        
        switch ($Action.ToLower()) {
            "dashboard" { 
                Show-OptimizationDashboard 
            }
            "scan" { 
                $duplicateDatabase = Scan-ComprehensiveDuplicates -DeepScan:$DeepScan
                Write-OptimizationLog "Scan completed. Found $($duplicateDatabase.duplicateGroups.Count) duplicate groups" "SUCCESS"
                return $duplicateDatabase
            }
            "analyze" { 
                $duplicateDatabase = Scan-ComprehensiveDuplicates
                $optimizationAnalysis = Calculate-OptimizationPotential -DuplicateDatabase $duplicateDatabase
                Write-OptimizationLog "Analysis completed. Potential space savings: $([math]::Round($optimizationAnalysis.totalSpaceWasted / 1MB, 2)) MB" "SUCCESS"
                return $optimizationAnalysis
            }
            "preview" { 
                $duplicateDatabase = Scan-ComprehensiveDuplicates
                $optimizationAnalysis = Calculate-OptimizationPotential -DuplicateDatabase $duplicateDatabase
                $eliminationResults = Execute-RedundancyElimination -DuplicateDatabase $duplicateDatabase -WhatIf:$true
                Write-OptimizationLog "Preview completed. Would reclaim: $([math]::Round($eliminationResults.spaceReclaimed / 1MB, 2)) MB" "SUCCESS"
                return $eliminationResults
            }
            "execute" { 
                $duplicateDatabase = Scan-ComprehensiveDuplicates
                $optimizationAnalysis = Calculate-OptimizationPotential -DuplicateDatabase $duplicateDatabase
                $eliminationResults = Execute-RedundancyElimination -DuplicateDatabase $duplicateDatabase -WhatIf:$false -BackupFirst
                $finalReport = Generate-OptimizationReport -EliminationResults $eliminationResults -OptimizationAnalysis $optimizationAnalysis
                Write-OptimizationLog "Optimization completed successfully!" "SUCCESS"
                return $finalReport
            }
            "clean" { 
                $removedDirs = Remove-EmptyDirectories -BasePath "$UNIFIED_DIR\templates"
                Write-OptimizationLog "Cleaned $($removedDirs.Count) empty directories" "SUCCESS"
                return $removedDirs
            }
            default { 
                Write-OptimizationLog "Unknown action: $Action" "ERROR"
                Show-OptimizationDashboard
            }
        }
    }
    catch {
        Write-OptimizationLog "Critical optimization error: $($_.Exception.Message)" "ERROR"
        Write-OptimizationLog "Stack trace: $($_.ScriptStackTrace)" "ERROR"
        return $null
    }
}

# Execute main function with parameters
if ($args.Count -gt 0) {
    $action = $args[0]
    $deepScan = $args -contains "-DeepScan"
    $whatIf = $args -contains "-WhatIf"
    
    Main -Action $action -DeepScan:$deepScan -WhatIf:$whatIf
}
else {
    Main -Action "dashboard"
}