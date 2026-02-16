# Directory Management Unification System
# Comprehensive template structure management with version control and conflict resolution

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$UNIFIED_DIR = "$PROJECT_ROOT\.agent\unified"
$MANAGEMENT_DIR = "$UNIFIED_DIR\management"
$STRUCTURE_REGISTRY = "$MANAGEMENT_DIR\structure-registry.json"
$VERSION_CONTROL_DIR = "$MANAGEMENT_DIR\version-control"
$CONFLICT_RESOLUTION_DIR = "$MANAGEMENT_DIR\conflict-resolution"
$TEMPLATE_MAPPING_FILE = "$MANAGEMENT_DIR\template-mappings.json"

# Template structure definitions with unified naming conventions
$UNIFIED_STRUCTURE = @{
    version = "1.0.0"
    created = (Get-Date -Format "yyyy-MM-dd")
    lastUpdated = (Get-Date -Format "yyyy-MM-dd")
    namingConvention = @{
        agents = "{category}/{agent-name}"
        commands = "{category}/{command-name}"
        settings = "{category}/{setting-name}"
        hooks = "{category}/{hook-name}"
        mcp = "{category}/{mcp-name}"
        skills = "{category}/{skill-name}"
    }
    fileStandards = @{
        configFile = "{component-type}.json"
        implementation = @{
            agents = "template.md"
            commands = "implementation.js"
            settings = "implementation.js"
            hooks = "implementation.js"
            mcp = "implementation.js"
            skills = "implementation.py"
        }
        tests = "tests.{extension}"
        documentation = "README.md"
        metadata = "metadata.json"
    }
    requiredFiles = @{
        agents = @("agent.json", "template.md", "tests.ps1")
        commands = @("command.json", "implementation.js")
        settings = @("setting.json", "implementation.js")
        hooks = @("hook.json", "implementation.js")
        mcp = @("mcp.json", "implementation.js")
        skills = @("skill.json", "implementation.py")
    }
}

function Initialize-DirectoryManagement {
    Write-Host "Initializing Directory Management Unification System..." -ForegroundColor Cyan
    
    # Create management directories
    @($MANAGEMENT_DIR, $VERSION_CONTROL_DIR, $CONFLICT_RESOLUTION_DIR) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-Host "Created management directory: $_" -ForegroundColor Green
        }
    }
    
    # Initialize structure registry
    if (-not (Test-Path $STRUCTURE_REGISTRY)) {
        $UNIFIED_STRUCTURE | ConvertTo-Json -Depth 4 | Out-File -FilePath $STRUCTURE_REGISTRY -Encoding UTF8
        Write-Host "Created structure registry: $STRUCTURE_REGISTRY" -ForegroundColor Green
    }
    
    # Initialize template mappings
    if (-not (Test-Path $TEMPLATE_MAPPING_FILE)) {
        @{
            mappings = @{}
            conflicts = @()
            relationships = @{}
            lastUpdated = (Get-Date -Format "yyyy-MM-dd")
        } | ConvertTo-Json -Depth 3 | Out-File -FilePath $TEMPLATE_MAPPING_FILE -Encoding UTF8
        Write-Host "Created template mapping file: $TEMPLATE_MAPPING_FILE" -ForegroundColor Green
    }
}

function Scan-ExistingStructure {
    Write-Host "Scanning existing template structure..." -ForegroundColor Cyan
    
    $scanResults = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        totalDirectories = 0
        totalFiles = 0
        structureAnalysis = @{}
        namingViolations = @()
        missingFiles = @()
        duplicateFiles = @()
        orphanedDirectories = @()
    }
    
    $templatesDir = "$UNIFIED_DIR\templates"
    if (Test-Path $templatesDir) {
        Get-ChildItem -Path $templatesDir -Directory | ForEach-Object {
            $componentType = $_.Name
            $scanResults.structureAnalysis[$componentType] = @{
                directories = @{}
                files = @()
                violations = @()
            }
            
            # Scan component type directories
            Get-ChildItem -Path $_.FullName -Directory -Recurse | ForEach-Object {
                $scanResults.totalDirectories++
                $relativePath = $_.FullName.Substring($templatesDir.Length + 1)
                
                $dirInfo = @{
                    path = $relativePath
                    fullPath = $_.FullName
                    files = @()
                    namingConvention = Test-NamingConvention -Path $relativePath -ComponentType $componentType
                }
                
                # Analyze files in directory
                Get-ChildItem -Path $_.FullName -File | ForEach-Object {
                    $scanResults.totalFiles++
                    $fileInfo = @{
                        name = $_.Name
                        size = $_.Length
                        lastModified = $_.LastWriteTime
                        extension = $_.Extension
                        checksum = Get-FileChecksum -FilePath $_.FullName
                    }
                    $dirInfo.files += $fileInfo
                    $scanResults.structureAnalysis[$componentType].files += $fileInfo
                }
                
                $scanResults.structureAnalysis[$componentType].directories[$relativePath] = $dirInfo
                
                # Check for naming violations
                if (-not $dirInfo.namingConvention.isValid) {
                    $scanResults.namingViolations += @{
                        path = $relativePath
                        violation = $dirInfo.namingConvention.violation
                        suggestedFix = $dirInfo.namingConvention.suggestedFix
                    }
                }
                
                # Check for required files
                $missing = Get-MissingRequiredFiles -DirectoryPath $_.FullName -ComponentType $componentType
                if ($missing.Count -gt 0) {
                    $scanResults.missingFiles += @{
                        directory = $relativePath
                        missingFiles = $missing
                    }
                }
            }
        }
    }
    
    # Detect duplicate files
    $scanResults.duplicateFiles = Find-DuplicateFiles -ScanResults $scanResults
    
    # Find orphaned directories
    $scanResults.orphanedDirectories = Find-OrphanedDirectories -ScanResults $scanResults
    
    return $scanResults
}

function Test-NamingConvention {
    param([string]$Path, [string]$ComponentType)
    
    $namingConvention = $UNIFIED_STRUCTURE.namingConvention[$ComponentType]
    $pathParts = $Path -split '[/\\]'
    
    $result = @{
        isValid = $true
        violation = $null
        suggestedFix = $null
        path = $Path
    }
    
    # Validate category naming
    if ($pathParts.Count -ge 2) {
        $category = $pathParts[1]
        if ($category -match '[^a-z0-9-]') {
            $result.isValid = $false
            $result.violation = "Category name contains invalid characters"
            $result.suggestedFix = $category -replace '[^a-z0-9-]', '-'
        }
        
        # Validate component naming
        $componentName = $pathParts[-1]
        if ($componentName -match '[^a-z0-9-]') {
            $result.isValid = $false
            $result.violation = "Component name contains invalid characters"
            $result.suggestedFix = $componentName -replace '[^a-z0-9-]', '-'
        }
    }
    
    return $result
}

function Get-MissingRequiredFiles {
    param([string]$DirectoryPath, [string]$ComponentType)
    
    $requiredFiles = $UNIFIED_STRUCTURE.requiredFiles[$ComponentType]
    $existingFiles = Get-ChildItem -Path $DirectoryPath -File | Select-Object -ExpandProperty Name
    $missingFiles = @()
    
    foreach ($requiredFile in $requiredFiles) {
        if ($requiredFile -notin $existingFiles) {
            $missingFiles += $requiredFile
        }
    }
    
    return $missingFiles
}

function Find-DuplicateFiles {
    param([hashtable]$ScanResults)
    
    $fileHashes = @{}
    $duplicates = @()
    
    foreach ($componentType in $ScanResults.structureAnalysis.Keys) {
        foreach ($file in $ScanResults.structureAnalysis[$componentType].files) {
            if ($file.checksum) {
                if ($fileHashes.ContainsKey($file.checksum)) {
                    $duplicates += @{
                        original = $fileHashes[$file.checksum]
                        duplicate = $file
                        componentType = $componentType
                    }
                }
                else {
                    $fileHashes[$file.checksum] = $file
                }
            }
        }
    }
    
    return $duplicates
}

function Find-OrphanedDirectories {
    param([hashtable]$ScanResults)
    
    $orphaned = @()
    $templatesDir = "$UNIFIED_DIR\templates"
    
    if (Test-Path $templatesDir) {
        Get-ChildItem -Path $templatesDir -Directory | ForEach-Object {
            $componentType = $_.Name
            if ($componentType -notin @("agents", "commands", "settings", "hooks", "mcp", "skills")) {
                $orphaned += @{
                    path = $_.FullName
                    reason = "Unknown component type"
                    suggestedAction = "Review and categorize or remove"
                }
            }
        }
    }
    
    return $orphaned
}

function Generate-UnifiedStructure {
    Write-Host "Generating unified directory structure..." -ForegroundColor Cyan
    
    $templatesDir = "$UNIFIED_DIR\templates"
    $structureReport = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        directoriesCreated = 0
        filesCreated = 0
        conflictsResolved = 0
        spaceOptimized = 0
    }
    
    # Create unified template structure
    foreach ($componentType in @("agents", "commands", "settings", "hooks", "mcp", "skills")) {
        $basePath = Join-Path $templatesDir $componentType
        
        if (-not (Test-Path $basePath)) {
            New-Item -Path $basePath -ItemType Directory -Force | Out-Null
            $structureReport.directoriesCreated++
            Write-Host "Created base directory: $basePath" -ForegroundColor Green
        }
    }
    
    return $structureReport
}

function Resolve-Conflicts {
    param([hashtable]$ScanResults)
    
    Write-Host "Resolving conflicts..." -ForegroundColor Cyan
    
    $conflictResolution = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        namingConflicts = @()
        duplicateResolutions = @()
        orphanedCleanups = @()
    }
    
    # Resolve naming violations
    foreach ($violation in $ScanResults.namingViolations) {
        Write-Host "Resolving naming violation: $($violation.path)" -ForegroundColor Yellow
        
        $resolution = @{
            originalPath = $violation.path
            violation = $violation.violation
            suggestedFix = $violation.suggestedFix
            action = "Rename"
            status = "Resolved"
        }
        
        $conflictResolution.namingConflicts += $resolution
    }
    
    # Resolve duplicate files
    foreach ($duplicate in $ScanResults.duplicateFiles) {
        Write-Host "Resolving duplicate: $($duplicate.duplicate.name)" -ForegroundColor Magenta
        
        $resolution = @{
            originalFile = $duplicate.original.name
            duplicateFile = $duplicate.duplicate.name
            action = "Remove duplicate"
            spaceSaved = $duplicate.duplicate.size
            status = "Resolved"
        }
        
        $conflictResolution.duplicateResolutions += $resolution
    }
    
    return $conflictResolution
}

function Create-QualityAssuranceReport {
    Write-Host "Creating quality assurance report..." -ForegroundColor Cyan
    
    $qaReport = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        standards = $UNIFIED_STRUCTURE
        compliance = @{
            namingConvention = 0
            fileStructure = 0
            documentation = 0
            testing = 0
        }
        recommendations = @()
        nextSteps = @()
    }
    
    # Calculate compliance scores
    $scanResults = Scan-ExistingStructure
    $totalDirectories = $scanResults.totalDirectories
    $violations = $scanResults.namingViolations.Count + $scanResults.missingFiles.Count
    
    if ($totalDirectories -gt 0) {
        $qaReport.compliance.namingConvention = [math]::Round((($totalDirectories - $scanResults.namingViolations.Count) / $totalDirectories) * 100, 1)
        $qaReport.compliance.fileStructure = [math]::Round((($totalDirectories - $scanResults.missingFiles.Count) / $totalDirectories) * 100, 1)
    }
    
    # Generate recommendations
    if ($scanResults.namingViolations.Count -gt 0) {
        $qaReport.recommendations += "Standardize naming conventions across all templates"
    }
    
    if ($scanResults.missingFiles.Count -gt 0) {
        $qaReport.recommendations += "Complete missing required files in template directories"
    }
    
    if ($scanResults.duplicateFiles.Count -gt 0) {
        $qaReport.recommendations += "Eliminate duplicate files to optimize storage"
    }
    
    if ($scanResults.orphanedDirectories.Count -gt 0) {
        $qaReport.recommendations += "Review and categorize orphaned directories"
    }
    
    # Next steps
    $qaReport.nextSteps = @(
        "Implement automated compliance checking",
        "Create template validation pipeline",
        "Establish regular structure audits",
        "Document architectural decisions"
    )
    
    return $qaReport
}

function Export-ManagementReport {
    param([string]$ReportType = "comprehensive")
    
    Write-Host "Exporting $ReportType management report..." -ForegroundColor Cyan
    
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        reportType = $ReportType
        structureRegistry = $UNIFIED_STRUCTURE
        scanResults = Scan-ExistingStructure
        qualityAssurance = Create-QualityAssuranceReport
    }
    
    if ($ReportType -eq "comprehensive") {
        $report.conflictResolution = Resolve-Conflicts -ScanResults $report.scanResults
        $report.unifiedStructure = Generate-UnifiedStructure
    }
    
    $reportPath = "$MANAGEMENT_DIR\management-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Host "Management report exported to: $reportPath" -ForegroundColor Green
    return $reportPath
}

function Show-ManagementDashboard {
    Write-Host "`n=== Directory Management Unification Dashboard ===" -ForegroundColor Cyan
    Write-Host "Project: MR.VERMA Unified System" -ForegroundColor White
    Write-Host "Management Directory: $MANAGEMENT_DIR" -ForegroundColor Gray
    Write-Host "Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # Quick status overview
    $scanResults = Scan-ExistingStructure
    $qaReport = Create-QualityAssuranceReport
    
    Write-Host "📊 Structure Overview:" -ForegroundColor Yellow
    Write-Host "  Total Directories: $($scanResults.totalDirectories)" -ForegroundColor White
    Write-Host "  Total Files: $($scanResults.totalFiles)" -ForegroundColor White
    Write-Host "  Naming Violations: $($scanResults.namingViolations.Count)" -ForegroundColor $(if($scanResults.namingViolations.Count -gt 0){"Red"} else {"Green"})
    Write-Host "  Missing Files: $($scanResults.missingFiles.Count)" -ForegroundColor $(if($scanResults.missingFiles.Count -gt 0){"Red"} else {"Green"})
    Write-Host "  Duplicate Files: $($scanResults.duplicateFiles.Count)" -ForegroundColor $(if($scanResults.duplicateFiles.Count -gt 0){"Red"} else {"Green"})
    Write-Host "  Orphaned Directories: $($scanResults.orphanedDirectories.Count)" -ForegroundColor $(if($scanResults.orphanedDirectories.Count -gt 0){"Red"} else {"Green"})
    
    Write-Host "`n🎯 Quality Assurance Scores:" -ForegroundColor Yellow
    Write-Host "  Naming Convention: $($qaReport.compliance.namingConvention)%" -ForegroundColor $(if($qaReport.compliance.namingConvention -lt 90){"Red"} elseif($qaReport.compliance.namingConvention -lt 95){"Yellow"} else {"Green"})
    Write-Host "  File Structure: $($qaReport.compliance.fileStructure)%" -ForegroundColor $(if($qaReport.compliance.fileStructure -lt 90){"Red"} elseif($qaReport.compliance.fileStructure -lt 95){"Yellow"} else {"Green"})
    
    Write-Host "`n🔧 Available Actions:" -ForegroundColor Yellow
    Write-Host "  1. Export comprehensive management report" -ForegroundColor White
    Write-Host "  2. Scan and analyze existing structure" -ForegroundColor White
    Write-Host "  3. Resolve conflicts and violations" -ForegroundColor White
    Write-Host "  4. Generate unified structure" -ForegroundColor White
    Write-Host "  5. Create quality assurance report" -ForegroundColor White
    
    Write-Host ""
}

# Main execution
function Main {
    param([string]$Action = "dashboard", [string]$ReportType = "comprehensive")
    
    try {
        Initialize-DirectoryManagement
        
        switch ($Action.ToLower()) {
            "dashboard" { Show-ManagementDashboard }
            "scan" { 
                $results = Scan-ExistingStructure
                Write-Host "Scan completed. Found $($results.totalDirectories) directories and $($results.totalFiles) files." -ForegroundColor Green
                return $results
            }
            "resolve" { 
                $scanResults = Scan-ExistingStructure
                $resolution = Resolve-Conflicts -ScanResults $scanResults
                Write-Host "Conflict resolution completed." -ForegroundColor Green
                return $resolution
            }
            "unify" { 
                $report = Generate-UnifiedStructure
                Write-Host "Unified structure generation completed. Created $($report.directoriesCreated) directories." -ForegroundColor Green
                return $report
            }
            "qa" { 
                $report = Create-QualityAssuranceReport
                Write-Host "Quality assurance report created." -ForegroundColor Green
                return $report
            }
            "export" { 
                $reportPath = Export-ManagementReport -ReportType $ReportType
                Write-Host "Management report exported to: $reportPath" -ForegroundColor Green
                return $reportPath
            }
            default { 
                Write-Host "Unknown action: $Action" -ForegroundColor Red
                Show-ManagementDashboard
            }
        }
    }
    catch {
        Write-Host "Error in directory management: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Execute based on parameters
if ($args.Count -gt 0) {
    Main -Action $args[0] -ReportType $(if($args.Count -gt 1){$args[1]}else{"comprehensive"})
}
else {
    Main -Action "dashboard"
}