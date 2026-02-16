# Simple Quality Assurance Framework
param([string]$Action = "test-all")

# Configuration
$UNIFIED_DIR = "e:\ABHINAV\MR.VERMA\.agent\unified"
$TEMPLATES_DIR = "$UNIFIED_DIR\templates"
$QA_REPORT = "$UNIFIED_DIR\config\qa-report.json"

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

function Test-TemplateStructure {
    param([string]$TemplatePath, [string]$ComponentType)
    
    $result = @{
        path = $TemplatePath
        type = $ComponentType
        passed = $false
        issues = @()
    }
    
    if (-not (Test-Path $TemplatePath)) {
        $result.issues += "Directory does not exist"
        return $result
    }
    
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
    
    $existingFiles = Get-ChildItem -Path $TemplatePath -File | Select-Object -ExpandProperty Name
    
    foreach ($requiredFile in $requiredFiles) {
        if ($requiredFile -in $existingFiles) {
            # Basic file validation
            $filePath = Join-Path $TemplatePath $requiredFile
            $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
            if ([string]::IsNullOrEmpty($content)) {
                $result.issues += "File $requiredFile is empty"
            }
        } else {
            $result.issues += "Missing required file: $requiredFile"
        }
    }
    
    $result.passed = $result.issues.Count -eq 0
    return $result
}

function Test-AllTemplates {
    Write-Log "Starting template quality assurance testing..." "INFO"
    
    $allResults = @()
    
    # Test each component type
    $componentTypes = @("agents", "commands", "settings", "hooks", "mcp", "skills")
    
    foreach ($componentType in $componentTypes) {
        $typePath = Join-Path $TEMPLATES_DIR $componentType
        
        if (Test-Path $typePath) {
            Write-Log "Testing $componentType components..." "INFO"
            
            $components = Get-ChildItem -Path $typePath -Directory -ErrorAction SilentlyContinue
            
            foreach ($component in $components) {
                $stats.totalComponents++
                $componentName = $component.Name
                $componentPath = $component.FullName
                
                Write-Log "Testing component: $componentName" "TEST"
                
                $testResult = Test-TemplateStructure -TemplatePath $componentPath -ComponentType $componentType
                $testResult.componentName = $componentName
                $testResult.componentType = $componentType
                
                if ($testResult.passed) {
                    $stats.passed++
                    Write-Log "PASSED: $componentName" "SUCCESS"
                } else {
                    $stats.failed++
                    Write-Log "FAILED: $componentName - Issues: $($testResult.issues -join ', ')" "ERROR"
                }
                
                $allResults += $testResult
            }
        } else {
            Write-Log "Directory not found: $typePath" "WARNING"
        }
    }
    
    return $allResults
}

function Generate-Report {
    param([array]$TestResults)
    
    Write-Log "Generating QA report..." "INFO"
    
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
    }
    
    foreach ($result in $TestResults) {
        if ($result.passed) {
            $report.passedComponents += @{
                name = $result.componentName
                type = $result.componentType
                path = $result.path
            }
        } else {
            $report.failedComponents += @{
                name = $result.componentName
                type = $result.componentType
                path = $result.path
                issues = $result.issues
            }
        }
    }
    
    # Save report
    $report | ConvertTo-Json -Depth 3 | Out-File -FilePath $QA_REPORT -Encoding UTF8
    Write-Log "QA report saved to: $QA_REPORT" "SUCCESS"
    
    return $report
}

# Main execution
switch ($Action.ToLower()) {
    "test-all" {
        $results = Test-AllTemplates
        $report = Generate-Report -TestResults $results
        
        Write-Log "=" "INFO"
        Write-Log "QA TESTING COMPLETED" "INFO"
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
    }
    default {
        Write-Log "Unknown action: $Action" "ERROR"
        Write-Log "Available actions: test-all" "INFO"
    }
}