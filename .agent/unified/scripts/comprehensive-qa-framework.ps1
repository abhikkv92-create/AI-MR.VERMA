# Comprehensive Template QA Framework
param([string]$Action = "test-all")

# Configuration
$UNIFIED_DIR = "e:\ABHINAV\MR.VERMA\.agent\unified"
$TEMPLATES_DIR = "$UNIFIED_DIR\templates"
$QA_REPORT = "$UNIFIED_DIR\config\comprehensive-qa-report.json"

# Statistics
$stats = @{
    totalComponents = 0
    passed = 0
    failed = 0
    errors = @()
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
}

function Test-ComponentFiles {
    param([string]$ComponentPath, [string]$ComponentType)
    
    $result = @{
        path = $ComponentPath
        type = $ComponentType
        passed = $false
        issues = @()
        files = @()
    }
    
    if (-not (Test-Path $ComponentPath)) {
        $result.issues += "Directory does not exist"
        return $result
    }
    
    # Get all files in the component directory
    $allFiles = Get-ChildItem -Path $ComponentPath -File -Recurse
    $result.files = $allFiles | Select-Object Name, FullName, Length
    
    # Check for required files based on component type
    $requiredFiles = switch ($ComponentType) {
        "agents" { @("agent.json", "implementation.py", "template.md") }
        "commands" { @("command.json", "implementation.js") }
        "settings" { @("setting.json", "implementation.js") }
        "hooks" { @("hook.json", "implementation.js") }
        "mcp" { @("mcp.json", "implementation.js") }
        "skills" { @("skill.json", "implementation.py") }
        default { @() }
    }
    
    # Check if required files exist anywhere in the directory tree
    $fileNames = $allFiles | Select-Object -ExpandProperty Name
    
    foreach ($requiredFile in $requiredFiles) {
        if ($requiredFile -in $fileNames) {
            # Find the actual file and validate it
            $actualFile = $allFiles | Where-Object { $_.Name -eq $requiredFile }
            if ($actualFile.Length -eq 0) {
                $result.issues += "File $requiredFile is empty"
            } else {
                # Basic content validation
                $content = Get-Content $actualFile.FullName -Raw -ErrorAction SilentlyContinue
                if ([string]::IsNullOrWhiteSpace($content)) {
                    $result.issues += "File $requiredFile is empty or whitespace"
                }
            }
        } else {
            $result.issues += "Missing required file: $requiredFile"
        }
    }
    
    # Additional validation for JSON files
    $jsonFiles = $allFiles | Where-Object { $_.Extension -eq ".json" }
    foreach ($jsonFile in $jsonFiles) {
        try {
            $content = Get-Content $jsonFile.FullName -Raw
            $null = $content | ConvertFrom-Json
        }
        catch {
            $result.issues += "Invalid JSON in file: $($jsonFile.Name)"
        }
    }
    
    $result.passed = $result.issues.Count -eq 0
    return $result
}

function Find-Components {
    param([string]$BasePath, [string]$ComponentType)
    
    $components = @()
    $baseDir = Join-Path $BasePath $ComponentType
    
    if (Test-Path $baseDir) {
        # Look for actual component directories (those containing required files)
        $allDirs = Get-ChildItem -Path $baseDir -Directory -Recurse
        
        foreach ($dir in $allDirs) {
            $files = Get-ChildItem -Path $dir.FullName -File -Recurse
            $hasRequiredFiles = $false
            
            # Check if this directory contains any required files for this component type
            $fileNames = $files | Select-Object -ExpandProperty Name
            $requiredPatterns = switch ($ComponentType) {
                "agents" { @("agent.json", "implementation.py") }
                "commands" { @("command.json", "implementation.js") }
                "settings" { @("setting.json", "implementation.js") }
                "hooks" { @("hook.json", "implementation.js") }
                "mcp" { @("mcp.json", "implementation.js") }
                "skills" { @("skill.json", "implementation.py") }
                default { @() }
            }
            
            foreach ($pattern in $requiredPatterns) {
                if ($pattern -in $fileNames) {
                    $hasRequiredFiles = $true
                    break
                }
            }
            
            if ($hasRequiredFiles) {
                $components += @{
                    name = $dir.Name
                    path = $dir.FullName
                    type = $ComponentType
                }
            }
        }
    }
    
    return $components
}

function Test-AllComponents {
    Write-Log "Starting comprehensive template quality assurance testing..." "INFO"
    
    $allResults = @()
    
    # Test each component type
    $componentTypes = @("agents", "commands", "settings", "hooks", "mcp", "skills")
    
    foreach ($componentType in $componentTypes) {
        Write-Log "Testing $componentType components..." "INFO"
        
        $components = Find-Components -BasePath $TEMPLATES_DIR -ComponentType $componentType
        
        if ($components.Count -eq 0) {
            Write-Log "No valid $componentType components found" "WARNING"
            continue
        }
        
        Write-Log "Found $($components.Count) $componentType components" "INFO"
        
        foreach ($component in $components) {
            $stats.totalComponents++
            
            Write-Log "Testing component: $($component.name)" "TEST"
            
            $testResult = Test-ComponentFiles -ComponentPath $component.path -ComponentType $componentType
            $testResult.componentName = $component.name
            $testResult.componentType = $componentType
            
            if ($testResult.passed) {
                $stats.passed++
                Write-Log "PASSED: $($component.name)" "SUCCESS"
            } else {
                $stats.failed++
                Write-Log "FAILED: $($component.name) - Issues: $($testResult.issues -join ', ')" "ERROR"
            }
            
            $allResults += $testResult
        }
    }
    
    return $allResults
}

function Generate-Report {
    param([array]$TestResults)
    
    Write-Log "Generating comprehensive QA report..." "INFO"
    
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        summary = @{
            totalComponents = $stats.totalComponents
            passed = $stats.passed
            failed = $stats.failed
            passRate = if ($stats.totalComponents -gt 0) { [math]::Round(($stats.passed / $stats.totalComponents) * 100, 1) } else { 0 }
        }
        failedComponents = @()
        passedComponents = @()
        componentDetails = @()
    }
    
    foreach ($result in $TestResults) {
        $componentInfo = @{
            name = $result.componentName
            type = $result.componentType
            path = $result.path
            passed = $result.passed
            issues = $result.issues
            fileCount = $result.files.Count
        }
        
        $report.componentDetails += $componentInfo
        
        if ($result.passed) {
            $report.passedComponents += $componentInfo
        } else {
            $report.failedComponents += $componentInfo
        }
    }
    
    # Save report
    $report | ConvertTo-Json -Depth 4 | Out-File -FilePath $QA_REPORT -Encoding UTF8
    Write-Log "QA report saved to: $QA_REPORT" "SUCCESS"
    
    return $report
}

# Main execution
switch ($Action.ToLower()) {
    "test-all" {
        $results = Test-AllComponents
        $report = Generate-Report -TestResults $results
        
        Write-Log "=" "INFO"
        Write-Log "COMPREHENSIVE QA TESTING COMPLETED" "INFO"
        Write-Log "=" "INFO"
        Write-Log "Total Components: $($report.summary.totalComponents)" "INFO"
        Write-Log "Passed: $($report.summary.passed)" "SUCCESS"
        Write-Log "Failed: $($report.summary.failed)" "ERROR"
        Write-Log "Pass Rate: $($report.summary.passRate)%" "INFO"
        Write-Log "Report: $QA_REPORT" "INFO"
        
        if ($report.summary.failed -gt 0) {
            Write-Log "Failed Components:" "ERROR"
            foreach ($failed in $report.failedComponents) {
                Write-Log "  - $($failed.name) ($($failed.type)): $($failed.issues -join ', ')" "ERROR"
            }
        }
        
        if ($report.summary.passed -gt 0) {
            Write-Log "Passed Components:" "SUCCESS"
            foreach ($passed in $report.passedComponents) {
                Write-Log "  - $($passed.name) ($($passed.type)) - $($passed.fileCount) files" "SUCCESS"
            }
        }
    }
    default {
        Write-Log "Unknown action: $Action" "ERROR"
        Write-Log "Available actions: test-all" "INFO"
    }
}