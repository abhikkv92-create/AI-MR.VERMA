# Quality Assurance and Automated Testing Framework
# Comprehensive validation, testing, and quality control system for templates

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$UNIFIED_DIR = "$PROJECT_ROOT\.agent\unified"
$QA_DIR = "$UNIFIED_DIR\quality-assurance"
$TEST_RESULTS_DIR = "$QA_DIR\test-results"
$VALIDATION_LOG = "$QA_DIR\validation.log"
$QA_REPORT = "$QA_DIR\qa-report.json"

# QA Standards and Compliance Matrix
$QA_STANDARDS = @{
    version = "1.0.0"
    standards = @{
        naming = @{
            pattern = "^[a-z0-9-]+$"
            maxLength = 50
            required = $true
            description = "Component names must be lowercase with hyphens only"
        }
        fileStructure = @{
            requiredFiles = @{
                agents = @("agent.json", "template.md", "tests.ps1")
                commands = @("command.json", "implementation.js")
                settings = @("setting.json", "implementation.js")
                hooks = @("hook.json", "implementation.js")
                mcp = @("mcp.json", "implementation.js")
                skills = @("skill.json", "implementation.py")
            }
            maxFileSize = 1MB
            encoding = "UTF-8"
        }
        content = @{
            jsonValidation = $true
            codeQuality = $true
            documentation = $true
            security = $true
        }
        performance = @{
            maxExecutionTime = 30
            memoryLimit = 100MB
            timeout = 300
        }
    }
    complianceLevels = @{
        excellent = 95
        good = 85
        acceptable = 70
        poor = 50
    }
}

# Test execution statistics
$qaStats = @{
    totalComponents = 0
    testsExecuted = 0
    testsPassed = 0
    testsFailed = 0
    complianceScore = 0
    executionTime = 0
    errors = @()
}

function Write-QALog {
    param(
        [string]$Message,
        [string]$Type = "INFO",
        [switch]$ConsoleOnly
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Type] $Message"
    
    # Console output with colors
    switch ($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "VALIDATION" { Write-Host $logEntry -ForegroundColor Cyan }
        "TEST" { Write-Host $logEntry -ForegroundColor Magenta }
        "COMPLIANCE" { Write-Host $logEntry -ForegroundColor Blue }
        default { Write-Host $logEntry -ForegroundColor White }
    }
    
    # File logging
    if (-not $ConsoleOnly) {
        Add-Content -Path $VALIDATION_LOG -Value $logEntry -ErrorAction SilentlyContinue
    }
}

function Initialize-QAEnvironment {
    Write-QALog "Initializing Quality Assurance Environment..." "VALIDATION"
    
    # Create QA directories
    @($QA_DIR, $TEST_RESULTS_DIR, "$QA_DIR\logs", "$QA_DIR\reports") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-QALog "Created QA directory: $_" "SUCCESS"
        }
    }
    
    # Initialize validation log
    "Quality Assurance Validation Log - $(Get-Date)" | Out-File -FilePath $VALIDATION_LOG -Force
    
    # Save QA standards
    $QA_STANDARDS | ConvertTo-Json -Depth 3 | Out-File -FilePath "$QA_DIR\qa-standards.json" -Encoding UTF8
    
    Write-QALog "QA environment initialized successfully" "SUCCESS"
}

function Test-NamingConvention {
    param([string]$ComponentName, [string]$ComponentPath)
    
    $testResult = @{
        test = "Naming Convention"
        component = $ComponentName
        path = $ComponentPath
        passed = $false
        score = 0
        details = @()
        recommendations = @()
    }
    
    # Test pattern compliance
    if ($ComponentName -match $QA_STANDARDS.standards.naming.pattern) {
        $testResult.score += 50
        $testResult.details += "[PASS] Pattern compliance: matches required format"
    }
    else {
        $testResult.details += "[FAIL] Pattern violation: contains invalid characters"
        $testResult.recommendations += "Use only lowercase letters, numbers, and hyphens"
    }
    
    # Test length compliance
    if ($ComponentName.Length -le $QA_STANDARDS.standards.naming.maxLength) {
        $testResult.score += 30
        $testResult.details += "[PASS] Length compliance: within maximum limit"
    }
    else {
        $testResult.details += "[FAIL] Length violation: exceeds maximum length"
        $testResult.recommendations += "Shorten component name to under $($QA_STANDARDS.standards.naming.maxLength) characters"
    }
    
    # Test semantic clarity
    if ($ComponentName -match "[a-z]{3,}" -and $ComponentName -match "-") {
        $testResult.score += 20
        $testResult.details += "[PASS] Semantic clarity: well-structured naming"
    }
    else {
        $testResult.details += "[WARN] Semantic warning: consider improving readability"
        $testResult.recommendations += "Use descriptive words separated by hyphens"
    }
    
    $testResult.passed = $testResult.score -ge 70
    return $testResult
}

function Test-FileStructure {
    param([string]$TemplatePath, [string]$ComponentType)
    
    $testResult = @{
        test = "File Structure"
        path = $TemplatePath
        type = $ComponentType
        passed = $false
        score = 0
        details = @()
        missingFiles = @()
        extraFiles = @()
    }
    
    if (-not (Test-Path $TemplatePath)) {
        $testResult.details += "[FAIL] Directory does not exist"
        return $testResult
    }
    
    $requiredFiles = $QA_STANDARDS.standards.fileStructure.requiredFiles[$ComponentType]
    $existingFiles = Get-ChildItem -Path $TemplatePath -File | Select-Object -ExpandProperty Name
    
    # Check for required files
    $foundRequired = 0
    foreach ($requiredFile in $requiredFiles) {
        if ($requiredFile -in $existingFiles) {
            $foundRequired++
            $testResult.details += "[PASS] Found required file: $requiredFile"
            
            # Validate file content
            $filePath = Join-Path $TemplatePath $requiredFile
            $fileValidation = Test-FileContent -FilePath $filePath -FileType $requiredFile
            if ($fileValidation.isValid) {
                $testResult.score += (80 / $requiredFiles.Count)
            }
            else {
                $testResult.details += "[WARN] File validation issues: $requiredFile - $($fileValidation.issues -join ', ')"
                $testResult.score += (40 / $requiredFiles.Count)
            }
        }
        else {
            $testResult.missingFiles += $requiredFile
            $testResult.details += "[FAIL] Missing required file: $requiredFile"
        }
    }
    
    # Check for extra files
    foreach ($existingFile in $existingFiles) {
        if ($existingFile -notin $requiredFiles) {
            $testResult.extraFiles += $existingFile
            $testResult.details += "Extra file found: $existingFile"
        }
    }
    
    # Check directory structure
    $subDirs = Get-ChildItem -Path $TemplatePath -Directory
    if ($subDirs.Count -eq 0) {
        $testResult.score += 10
        $testResult.details += "[PASS] Clean directory structure"
    }
    else {
        $testResult.score += 5
        $testResult.details += "Subdirectories found: $($subDirs.Count)"
    }
    
    $testResult.passed = $testResult.score -ge 70
    return $testResult
}

function Test-FileContent {
    param([string]$FilePath, [string]$FileType)
    
    $validation = @{
        isValid = $true
        issues = @()
        size = 0
        encoding = "Unknown"
    }
    
    try {
        if (Test-Path $FilePath) {
            $fileInfo = Get-Item $FilePath
            $validation.size = $fileInfo.Length
            
            # Check file size
            if ($validation.size -gt $QA_STANDARDS.standards.fileStructure.maxFileSize) {
                $validation.isValid = $false
                $validation.issues += "File size exceeds maximum limit"
            }
            
            # Check encoding
            $content = Get-Content $FilePath -Raw -ErrorAction Stop
            $validation.encoding = "UTF-8" # Assume UTF-8 for now
            
            # Type-specific validation
            switch ($FileType) {
                "*.json" {
                    try {
                        $jsonContent = $content | ConvertFrom-Json
                        $validation.details += "[PASS] Valid JSON structure"
                    }
                    catch {
                        $validation.isValid = $false
                        $validation.issues += "Invalid JSON format"
                    }
                }
                "*.js" {
                    # Basic JavaScript validation
                    if ($content -match "class\s+\w+" -or $content -match "function\s+\w+" -or $content -match "module\.exports") {
                        $validation.details += "[PASS] Basic JavaScript structure detected"
                    }
                    else {
                        $validation.issues += "No recognizable JavaScript patterns"
                    }
                }
                "*.py" {
                    # Basic Python validation
                    if ($content -match "class\s+\w+" -or $content -match "def\s+\w+" -or $content -match "import\s+\w+") {
                        $validation.details += "[PASS] Basic Python structure detected"
                    }
                    else {
                        $validation.issues += "No recognizable Python patterns"
                    }
                }
                "*.md" {
                    # Markdown validation
                    if ($content -match "^#+\s" -or $content -match "\*\*" -or $content -match "\[.*\]\(.*\)") {
                        $validation.details += "[PASS] Markdown formatting detected"
                    }
                }
            }
        }
        else {
            $validation.isValid = false
            $validation.issues += "File does not exist"
        }
    }
    catch {
        $validation.isValid = false
        $validation.issues += "Error reading file: $($_.Exception.Message)"
    }
    
    return $validation
}

function Test-ComponentIntegration {
    param([string]$ComponentPath, [string]$ComponentType)
    
    $integrationTest = @{
        test = "Component Integration"
        path = $ComponentPath
        type = $ComponentType
        passed = $false
        score = 0
        dependencies = @()
        conflicts = @()
        compatibility = @()
    }
    
    # Test JSON configuration integration
    $configFile = Get-ChildItem -Path $ComponentPath -Filter "*.json" | Select-Object -First 1
    if ($configFile) {
        try {
            $config = Get-Content $configFile.FullName -Raw | ConvertFrom-Json
            $integrationTest.dependencies = if ($config.requiredDependencies) { $config.requiredDependencies } else { @() }
            $integrationTest.compatibility += "[PASS] Configuration parsing successful"
            $integrationTest.score += 40
        }
        catch {
            $integrationTest.conflicts += "Configuration parsing failed"
            $integrationTest.score += 10
        }
    }
    
    # Test implementation file integration
    $implFiles = Get-ChildItem -Path $ComponentPath -Filter "implementation.*"
    if ($implFiles.Count -gt 0) {
        $integrationTest.compatibility += "[PASS] Implementation files found"
        $integrationTest.score += 30
        
        # Test syntax validation
        foreach ($implFile in $implFiles) {
            $syntaxValid = Test-ImplementationSyntax -FilePath $implFile.FullName -FileType $implFile.Extension
            if ($syntaxValid) {
                $integrationTest.compatibility += "[PASS] Syntax validation passed for $($implFile.Name)"
                $integrationTest.score += 15
            }
            else {
                $integrationTest.conflicts += "Syntax validation failed for $($implFile.Name)"
                $integrationTest.score += 5
            }
        }
    }
    else {
        $integrationTest.conflicts += "No implementation files found"
    }
    
    # Test documentation integration
    $docFiles = Get-ChildItem -Path $ComponentPath -Filter "*.md"
    if ($docFiles.Count -gt 0) {
        $integrationTest.compatibility += "[PASS] Documentation files found"
        $integrationTest.score += 15
    }
    else {
        $integrationTest.conflicts += "No documentation files found"
    }
    
    $integrationTest.passed = $integrationTest.score -ge 70
    return $integrationTest
}

function Test-ImplementationSyntax {
    param([string]$FilePath, [string]$FileType)
    
    try {
        $content = Get-Content $FilePath -Raw
        
        switch ($FileType) {
            ".js" {
                # Basic JavaScript syntax validation
                return $content -match "class\s+\w+" -or $content -match "function\s+\w+" -or $content -match "module\.exports"
            }
            ".py" {
                # Basic Python syntax validation
                return $content -match "class\s+\w+" -or $content -match "def\s+\w+" -or $content -match "import\s+\w+"
            }
            ".json" {
                try {
                    $content | ConvertFrom-Json | Out-Null
                    return $true
                }
                catch {
                    return $false
                }
            }
            default {
                return $true
            }
        }
    }
    catch {
        return $false
    }
}

function Test-PerformanceCharacteristics {
    param([string]$ComponentPath, [string]$ComponentType)
    
    $performanceTest = @{
        test = "Performance Characteristics"
        path = $ComponentPath
        type = $ComponentType
        passed = $false
        score = 0
        fileSize = 0
        complexity = "Unknown"
        loadTime = 0
        recommendations = @()
    }
    
    # Measure file sizes
    $files = Get-ChildItem -Path $ComponentPath -File
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $performanceTest.fileSize = $totalSize
    
    if ($totalSize -lt 100KB) {
        $performanceTest.score += 40
        $performanceTest.complexity = "Lightweight"
    }
    elseif ($totalSize -lt 500KB) {
        $performanceTest.score += 30
        $performanceTest.complexity = "Moderate"
    }
    else {
        $performanceTest.score += 20
        $performanceTest.complexity = "Heavy"
        $performanceTest.recommendations += "Consider reducing component size"
    }
    
    # Test loading performance
    $startTime = Get-Date
    
    # Simulate component loading
    try {
        $configFile = Get-ChildItem -Path $ComponentPath -Filter "*.json" | Select-Object -First 1
        if ($configFile) {
            $config = Get-Content $configFile.FullName -Raw | ConvertFrom-Json
        }
        $loadTime = ((Get-Date) - $startTime).TotalMilliseconds
        $performanceTest.loadTime = $loadTime
        
        if ($loadTime -lt 100) {
            $performanceTest.score += 30
        }
        elseif ($loadTime -lt 500) {
            $performanceTest.score += 20
        }
        else {
            $performanceTest.score += 10
            $performanceTest.recommendations += "Optimize component loading time"
        }
    }
    catch {
        $performanceTest.score += 10
        $performanceTest.recommendations += "Fix component loading issues"
    }
    
    # Check for performance-related configurations
    if ($config.timeout -or $config.maxMemory -or $config.optimization) {
        $performanceTest.score += 30
    }
    else {
        $performanceTest.recommendations += "Add performance configuration options"
    }
    
    $performanceTest.passed = $performanceTest.score -ge 70
    return $performanceTest
}

function Execute-ComponentTests {
    param([string]$TemplatePath, [string]$ComponentType, [string]$ComponentName)
    
    Write-QALog "Testing component: $ComponentName ($ComponentType)" "TEST"
    
    $testSuite = @{
        componentName = $ComponentName
        componentType = $ComponentType
        componentPath = $TemplatePath
        testTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        tests = @()
        overallScore = 0
        complianceLevel = "Unknown"
        passed = $false
        executionTime = 0
    }
    
    $startTime = Get-Date
    
    # Execute all test types
    $testSuite.tests += Test-NamingConvention -ComponentName $ComponentName -ComponentPath $TemplatePath
    $testSuite.tests += Test-FileStructure -TemplatePath $TemplatePath -ComponentType $ComponentType
    $testSuite.tests += Test-ComponentIntegration -ComponentPath $TemplatePath -ComponentType $ComponentType
    $testSuite.tests += Test-PerformanceCharacteristics -ComponentPath $TemplatePath -ComponentType $ComponentType
    
    $executionTime = (Get-Date) - $startTime
    $testSuite.executionTime = $executionTime.TotalSeconds
    
    # Calculate overall score
    if ($testSuite.tests.Count -gt 0) {
        $totalScore = 0
        foreach ($test in $testSuite.tests) {
            $totalScore += $test.score
        }
        $testSuite.overallScore = [math]::Round($totalScore / $testSuite.tests.Count, 1)
    } else {
        $testSuite.overallScore = 0
    }
    
    # Determine compliance level
    if ($testSuite.overallScore -ge $QA_STANDARDS.complianceLevels.excellent) {
        $testSuite.complianceLevel = "Excellent"
    }
    elseif ($testSuite.overallScore -ge $QA_STANDARDS.complianceLevels.good) {
        $testSuite.complianceLevel = "Good"
    }
    elseif ($testSuite.overallScore -ge $QA_STANDARDS.complianceLevels.acceptable) {
        $testSuite.complianceLevel = "Acceptable"
    }
    else {
        $testSuite.complianceLevel = "Poor"
    }
    
    $testSuite.passed = $testSuite.overallScore -ge $QA_STANDARDS.complianceLevels.acceptable
    
    # Update statistics
    $qaStats.testsExecuted += $testSuite.tests.Count
    $qaStats.testsPassed += ($testSuite.tests | Where-Object { $_.passed }).Count
    $qaStats.testsFailed += ($testSuite.tests | Where-Object { -not $_.passed }).Count
    
    Write-QALog "Component test completed: $ComponentName (Score: $($testSuite.overallScore)%, Level: $($testSuite.complianceLevel))" $(if($testSuite.passed){"SUCCESS"}else{"WARNING"})
    
    return $testSuite
}

function Test-AllTemplates {
    param([string]$TemplatesPath = "$UNIFIED_DIR\templates")
    
    Write-QALog "Starting comprehensive template testing..." "VALIDATION"
    
    $qaStats.totalComponents = 0
    $allTestResults = @()
    
    if (-not (Test-Path $TemplatesPath)) {
        Write-QALog "Templates path does not exist: $TemplatesPath" "ERROR"
        return $null
    }
    
    # Test each component type
    $componentTypes = @("agents", "commands", "settings", "hooks", "mcp", "skills")
    
    foreach ($componentType in $componentTypes) {
        $typePath = Join-Path $TemplatesPath $componentType
        
        if (Test-Path $typePath) {
            Write-QALog "Testing $componentType components..." "TEST"
            
            $components = Get-ChildItem -Path $typePath -Directory -ErrorAction SilentlyContinue
            
            foreach ($component in $components) {
                $qaStats.totalComponents++
                
                $componentName = $component.Name
                $componentPath = $component.FullName
                
                $testResult = Execute-ComponentTests -TemplatePath $componentPath -ComponentType $componentType -ComponentName $componentName
                $allTestResults += $testResult
                
                # Save individual test result
                $testResultPath = "$TEST_RESULTS_DIR\$componentType-$componentName-test-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
                $testResult | ConvertTo-Json -Depth 4 | Out-File -FilePath $testResultPath -Encoding UTF8
            }
        }
    }
    
    # Calculate overall QA statistics
    $qaStats.complianceScore = [math]::Round(($allTestResults | Where-Object { $_.passed }).Count / $allTestResults.Count * 100, 1)
    
    Write-QALog "Template testing completed. Tested $($qaStats.totalComponents) components with $($qaStats.complianceScore)% compliance" $(if($qaStats.complianceScore -ge 80){"SUCCESS"}else{"WARNING"})
    
    return $allTestResults
}

function Generate-QAReport {
    param([array]$TestResults)
    
    Write-QALog "Generating comprehensive QA report..." "VALIDATION"
    
    $report = @{
        reportTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        summary = @{
            totalComponents = $qaStats.totalComponents
            testsExecuted = $qaStats.testsExecuted
            testsPassed = $qaStats.testsPassed
            testsFailed = $qaStats.testsFailed
            complianceScore = $qaStats.complianceScore
            executionTime = $qaStats.executionTime
        }
        complianceBreakdown = @{
            excellent = ($TestResults | Where-Object { $_.complianceLevel -eq "Excellent" }).Count
            good = ($TestResults | Where-Object { $_.complianceLevel -eq "Good" }).Count
            acceptable = ($TestResults | Where-Object { $_.complianceLevel -eq "Acceptable" }).Count
            poor = ($TestResults | Where-Object { $_.complianceLevel -eq "Poor" }).Count
        }
        componentAnalysis = @{
            byType = @{}
            failedComponents = @()
            topPerformers = @()
            improvementNeeded = @()
        }
        recommendations = @()
        actionItems = @()
    }
    
    # Analyze by component type
    $componentTypes = $TestResults | Group-Object -Property componentType
    foreach ($group in $componentTypes) {
        $averageScore = 0
        if ($group.Group.Count -gt 0) {
            $totalScore = 0
            foreach ($item in $group.Group) {
                $totalScore += $item.overallScore
            }
            $averageScore = [math]::Round($totalScore / $group.Group.Count, 1)
        }
        
        $report.componentAnalysis.byType[$group.Name] = @{
            total = $group.Count
            passed = ($group.Group | Where-Object { $_.passed }).Count
            averageScore = $averageScore
            complianceLevel = ($group.Group | Group-Object -Property complianceLevel | Sort-Object Count -Descending | Select-Object -First 1).Name
        }
    }
    
    # Identify failed components
    $report.componentAnalysis.failedComponents = $TestResults | Where-Object { -not $_.passed } | ForEach-Object {
        @{
            name = $_.componentName
            type = $_.componentType
            score = $_.overallScore
            complianceLevel = $_.complianceLevel
            failedTests = ($_.tests | Where-Object { -not $_.passed }).test -join ", "
        }
    }
    
    # Identify top performers
    $report.componentAnalysis.topPerformers = $TestResults | Sort-Object overallScore -Descending | Select-Object -First 5 | ForEach-Object {
        @{
            name = $_.componentName
            type = $_.componentType
            score = $_.overallScore
            complianceLevel = $_.complianceLevel
        }
    }
    
    # Identify improvement needed
    $report.componentAnalysis.improvementNeeded = $TestResults | Where-Object { $_.overallScore -lt 80 } | ForEach-Object {
        @{
            name = $_.componentName
            type = $_.componentType
            score = $_.overallScore
            complianceLevel = $_.complianceLevel
            priority = if ($_.overallScore -lt 50) { "High" } elseif ($_.overallScore -lt 70) { "Medium" } else { "Low" }
        }
    }
    
    # Generate recommendations
    if ($report.summary.complianceScore -lt 90) {
        $report.recommendations += "Overall compliance is below 90%. Consider comprehensive review of all components."
    }
    
    if ($report.componentAnalysis.failedComponents.Count -gt 0) {
        $report.recommendations += "$($report.componentAnalysis.failedComponents.Count) components failed testing. Priority should be given to fixing these components."
    }
    
    if ($report.complianceBreakdown.poor -gt 0) {
        $report.recommendations += "$($report.complianceBreakdown.poor) components have poor compliance. These require immediate attention."
    }
    
    # Generate action items
    $report.actionItems = @(
        "Review and fix failed components",
        "Implement automated QA checks in CI/CD pipeline",
        "Establish regular QA testing schedule",
        "Create component improvement roadmap",
        "Document QA standards and best practices"
    )
    
    # Save report
    $report | ConvertTo-Json -Depth 4 | Out-File -FilePath $QA_REPORT -Encoding UTF8
    Write-QALog "QA report saved to: $QA_REPORT" "SUCCESS"
    
    return $report
}

function Show-QADashboard {
    Write-Host "`n=== Quality Assurance Dashboard ===" -ForegroundColor Cyan
    Write-Host "Project: MR.VERMA Unified System" -ForegroundColor White
    Write-Host "QA Directory: $QA_DIR" -ForegroundColor Gray
    Write-Host "Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
}
    
    Write-Host "[STATS] QA Statistics:" -ForegroundColor Yellow
    Write-Host "  Total Components Tested: $($qaStats.totalComponents)" -ForegroundColor White
    Write-Host "  Tests Executed: $($qaStats.testsExecuted)" -ForegroundColor White
    Write-Host "  Tests Passed: $($qaStats.testsPassed)" -ForegroundColor Green
    Write-Host "  Tests Failed: $($qaStats.testsFailed)" -ForegroundColor Red
    Write-Host "  Overall Compliance: $($qaStats.complianceScore)%" -ForegroundColor $(if($qaStats.complianceScore -ge 90){"Green"} elseif($qaStats.complianceScore -ge 70){"Yellow"} else{"Red"})
    Write-Host "  Execution Time: $([math]::Round($qaStats.executionTime, 1)) seconds" -ForegroundColor White
    
    Write-Host "`n[ACTIONS] Available Actions:" -ForegroundColor Yellow
    Write-Host "  1. Run comprehensive QA tests" -ForegroundColor White
    Write-Host "  2. Test specific component type" -ForegroundColor White
    Write-Host "  3. Generate QA report" -ForegroundColor White
    Write-Host "  4. Validate naming conventions" -ForegroundColor White
    Write-Host "  5. Check file structure compliance" -ForegroundColor White
    Write-Host "  6. Test component integration" -ForegroundColor White
    
    Write-Host ""

function Main {
    param([string]$Action = "dashboard", [string]$ComponentType = "", [string]$ComponentName = "")
    
    try {
        Initialize-QAEnvironment
        
        switch ($Action.ToLower()) {
            "dashboard" { 
                Show-QADashboard 
            }
            "test-all" { 
                $results = Test-AllTemplates
                $report = Generate-QAReport -TestResults $results
                Write-QALog "Comprehensive QA testing completed. Report generated with $($report.summary.totalComponents) components tested" "SUCCESS"
                return $report
            }
            "test-type" { 
                if ($ComponentType) {
                    $typePath = "$UNIFIED_DIR\templates\$ComponentType"
                    if (Test-Path $typePath) {
                        $results = @()
                        Get-ChildItem -Path $typePath -Directory | ForEach-Object {
                            $results += Execute-ComponentTests -TemplatePath $_.FullName -ComponentType $ComponentType -ComponentName $_.Name
                        }
                        Write-QALog "Testing of $ComponentType components completed. Tested $($results.Count) components" "SUCCESS"
                        return $results
                    }
                    else {
                        Write-QALog "Component type directory not found: $typePath" "ERROR"
                    }
                }
                else {
                    Write-QALog "Component type not specified" "ERROR"
                }
            }
            "validate-naming" { 
                if ($ComponentName) {
                    $result = Test-NamingConvention -ComponentName $ComponentName -ComponentPath ""
                    Write-QALog "Naming validation for ${ComponentName}: $($(if($result.passed){'PASSED'}else{'FAILED'})) (Score: $($result.score)%)" $(if($result.passed){"SUCCESS"}else{"WARNING"})
                    return $result
                }
                else {
                    Write-QALog "Component name not specified for naming validation" "ERROR"
                }
            }
            "validate-structure" { 
                if ($ComponentType -and $ComponentName) {
                    $componentPath = "$UNIFIED_DIR\templates\$ComponentType\$ComponentName"
                    if (Test-Path $componentPath) {
                        $result = Test-FileStructure -TemplatePath $componentPath -ComponentType $ComponentType
                        Write-QALog "Structure validation for ${ComponentName}: $($(if($result.passed){'PASSED'}else{'FAILED'})) (Score: $($result.score)%)" $(if($result.passed){"SUCCESS"}else{"WARNING"})
                        return $result
                    }
                    else {
                        Write-QALog "Component path not found: $componentPath" "ERROR"
                    }
                }
                else {
                    Write-QALog "Component type and name required for structure validation" "ERROR"
                }
            }
            default { 
                Write-QALog "Unknown action: $Action" "ERROR"
                Show-QADashboard
            }
        }
    }
    catch {
        Write-QALog "Critical QA error: $($_.Exception.Message)" "ERROR"
        Write-QALog "Stack trace: $($_.ScriptStackTrace)" "ERROR"
        return $null
    }
}

# Execute based on parameters
if ($args.Count -gt 0) {
    $action = $args[0]
    $componentType = if($args.Count -gt 1){$args[1]}else{""}
    $componentName = if($args.Count -gt 2){$args[2]}else{""}
    
    Main -Action $action -ComponentType $componentType -ComponentName $componentName
}
else {
    Main -Action "dashboard"
}