# Comprehensive Template Optimization Orchestrator
# Master script that coordinates all optimization, installation, and management tasks

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$UNIFIED_DIR = "$PROJECT_ROOT\.agent\unified"
$ORCHESTRATION_DIR = "$UNIFIED_DIR\orchestration"
$MASTER_LOG = "$ORCHESTRATION_DIR\master-orchestration.log"
$EXECUTION_REPORT = "$ORCHESTRATION_DIR\execution-report.json"

# Orchestration configuration
$ORCHESTRATION_CONFIG = @{
    version = "1.0.0"
    phases = @(
        @{
            name = "Pre-Installation Analysis"
            description = "Analyze existing structure and identify issues"
            scripts = @("directory-management-system.ps1")
            actions = @("scan", "analyze")
            critical = $true
        },
        @{
            name = "Redundancy Elimination"
            description = "Remove duplicates and optimize existing structure"
            scripts = @("redundancy-elimination-engine.ps1")
            actions = @("scan", "preview", "execute")
            critical = $false
        },
        @{
            name = "Template Installation"
            description = "Install missing templates with enhanced structure"
            scripts = @("enhanced-install-claude-templates.ps1")
            actions = @()
            critical = $true
        },
        @{
            name = "Quality Assurance"
            description = "Comprehensive testing and validation"
            scripts = @("quality-assurance-framework.ps1")
            actions = @("test-all")
            critical = $true
        },
        @{
            name = "Final Validation"
            description = "Complete system validation and reporting"
            scripts = @("validate-integration.ps1")
            actions = @()
            critical = $true
        }
    )
    options = @{
        backupBeforeChanges = $true
        createRollbackPoints = $true
        generateDetailedReports = $true
        stopOnCriticalFailure = $true
        parallelExecution = $false
    }
}

# Execution statistics
$orchestrationStats = @{
    startTime = $null
    endTime = $null
    totalPhases = 0
    completedPhases = 0
    failedPhases = 0
    skippedPhases = 0
    totalComponents = 0
    successfullyProcessed = 0
    errors = @()
    warnings = @()
}

function Write-OrchestrationLog {
    param(
        [string]$Message,
        [string]$Type = "INFO",
        [string]$Phase = "",
        [switch]$ConsoleOnly
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $phasePrefix = if ($Phase) { "[$Phase] " } else { "" }
    $logEntry = "[$timestamp] [$Type] $phasePrefix$Message"
    
    # Console output with colors
    switch ($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "PHASE" { Write-Host $logEntry -ForegroundColor Cyan }
        "ORCHESTRATION" { Write-Host $logEntry -ForegroundColor Magenta }
        "PROGRESS" { Write-Host $logEntry -ForegroundColor Blue }
        default { Write-Host $logEntry -ForegroundColor White }
    }
    
    # File logging
    if (-not $ConsoleOnly) {
        Add-Content -Path $MASTER_LOG -Value $logEntry -ErrorAction SilentlyContinue
    }
}

function Initialize-Orchestration {
    Write-OrchestrationLog "Initializing Comprehensive Template Optimization Orchestrator..." "ORCHESTRATION"
    
    # Create orchestration directories
    @($ORCHESTRATION_DIR, "$ORCHESTRATION_DIR\logs", "$ORCHESTRATION_DIR\reports", "$ORCHESTRATION_DIR\backups") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-OrchestrationLog "Created orchestration directory: $_" "SUCCESS"
        }
    }
    
    # Initialize master log
    "Master Orchestration Log - $(Get-Date)" | Out-File -FilePath $MASTER_LOG -Force
    
    # Save orchestration configuration
    $ORCHESTRATION_CONFIG | ConvertTo-Json -Depth 3 | Out-File -FilePath "$ORCHESTRATION_DIR\orchestration-config.json" -Encoding UTF8
    
    Write-OrchestrationLog "Orchestration environment initialized successfully" "SUCCESS"
}

function Execute-Phase {
    param(
        [hashtable]$Phase,
        [int]$PhaseNumber,
        [int]$TotalPhases
    )
    
    Write-OrchestrationLog "Starting Phase ${PhaseNumber}/${TotalPhases}: $($Phase.name)" "PHASE"
    Write-OrchestrationLog "Description: $($Phase.description)" "INFO" -Phase $Phase.name
    
    $phaseResult = @{
        name = $Phase.name
        startTime = Get-Date
        endTime = $null
        status = "Running"
        actions = @()
        errors = @()
        warnings = @()
        executionTime = 0
        details = @()
    }
    
    try {
        # Execute phase-specific actions
        foreach ($action in $Phase.actions) {
            Write-OrchestrationLog "Executing action: $action" "PROGRESS" -Phase $Phase.name
            
            $actionResult = Execute-PhaseAction -Phase $Phase -Action $action -PhaseName $Phase.name
            $phaseResult.actions += $actionResult
            
            if ($actionResult.status -eq "Failed" -and $Phase.critical) {
                throw "Critical action failed: $($actionResult.error)"
            }
        }
        
        # Execute main script if specified
        if ($Phase.scripts.Count -gt 0) {
            foreach ($script in $Phase.scripts) {
                Write-OrchestrationLog "Executing script: $script" "PROGRESS" -Phase $Phase.name
                
                $scriptPath = "$UNIFIED_DIR\scripts\$script"
                if (Test-Path $scriptPath) {
                    $scriptResult = Execute-Script -ScriptPath $scriptPath -PhaseName $Phase.name
                    $phaseResult.details += $scriptResult
                    
                    if ($scriptResult.status -eq "Failed" -and $Phase.critical) {
                        throw "Critical script failed: $($scriptResult.error)"
                    }
                }
                else {
                    $warning = "Script not found: $script"
                    Write-OrchestrationLog $warning "WARNING" -Phase $Phase.name
                    $phaseResult.warnings += $warning
                }
            }
        }
        
        $phaseResult.status = "Completed"
        $phaseResult.endTime = Get-Date
        $phaseResult.executionTime = ($phaseResult.endTime - $phaseResult.startTime).TotalSeconds
        
        Write-OrchestrationLog "Phase completed successfully in $($phaseResult.executionTime) seconds" "SUCCESS" -Phase $Phase.name
        
    }
    catch {
        $phaseResult.status = "Failed"
        $phaseResult.endTime = Get-Date
        $phaseResult.executionTime = ($phaseResult.endTime - $phaseResult.startTime).TotalSeconds
        $phaseResult.errors += $_.Exception.Message
        
        Write-OrchestrationLog "Phase failed: $($_.Exception.Message)" "ERROR" -Phase $Phase.name
        
        if ($Phase.critical -and $ORCHESTRATION_CONFIG.options.stopOnCriticalFailure) {
            throw
        }
    }
    
    return $phaseResult
}

function Execute-PhaseAction {
    param(
        [hashtable]$Phase,
        [string]$Action,
        [string]$PhaseName
    )
    
    $actionResult = @{
        action = $Action
        startTime = Get-Date
        endTime = $null
        status = "Running"
        result = $null
        error = $null
        executionTime = 0
    }
    
    try {
        switch ($Action) {
            "scan" {
                Write-OrchestrationLog "Scanning existing structure..." "PROGRESS" -Phase $PhaseName
                # Execute directory management scan
                $scanResult = & "$UNIFIED_DIR\scripts\directory-management-system.ps1" "scan"
                $actionResult.result = $scanResult
                Write-OrchestrationLog "Scan completed. Found $($scanResult.totalDirectories) directories and $($scanResult.totalFiles) files" "SUCCESS" -Phase $PhaseName
            }
            
            "analyze" {
                Write-OrchestrationLog "Analyzing structure for optimization opportunities..." "PROGRESS" -Phase $PhaseName
                # Execute analysis
                $analysisResult = & "$UNIFIED_DIR\scripts\directory-management-system.ps1" "analyze"
                $actionResult.result = $analysisResult
                Write-OrchestrationLog "Analysis completed" "SUCCESS" -Phase $PhaseName
            }
            
            "preview" {
                Write-OrchestrationLog "Previewing redundancy elimination..." "PROGRESS" -Phase $PhaseName
                # Execute preview
                $previewResult = & "$UNIFIED_DIR\scripts\redundancy-elimination-engine.ps1" "preview"
                $actionResult.result = $previewResult
                Write-OrchestrationLog "Preview completed. Would save $([math]::Round($previewResult.spaceReclaimed / 1MB, 2)) MB" "SUCCESS" -Phase $PhaseName
            }
            
            "execute" {
                Write-OrchestrationLog "Executing redundancy elimination..." "PROGRESS" -Phase $PhaseName
                # Execute elimination
                $eliminationResult = & "$UNIFIED_DIR\scripts\redundancy-elimination-engine.ps1" "execute"
                $actionResult.result = $eliminationResult
                Write-OrchestrationLog "Elimination completed. Removed $($eliminationResult.filesRemoved.Count) files" "SUCCESS" -Phase $PhaseName
            }
            
            "test-all" {
                Write-OrchestrationLog "Running comprehensive QA tests..." "PROGRESS" -Phase $PhaseName
                # Execute QA tests
                $qaResult = & "$UNIFIED_DIR\scripts\quality-assurance-framework.ps1" "test-all"
                $actionResult.result = $qaResult
                Write-OrchestrationLog "QA tests completed. Compliance score: $($qaResult.summary.complianceScore)%" "SUCCESS" -Phase $PhaseName
            }
            
            default {
                Write-OrchestrationLog "Unknown action: $Action" "WARNING" -Phase $PhaseName
                $actionResult.status = "Skipped"
            }
        }
        
        $actionResult.status = "Completed"
        
    }
    catch {
        $actionResult.status = "Failed"
        $actionResult.error = $_.Exception.Message
        Write-OrchestrationLog "Action failed: $($_.Exception.Message)" "ERROR" -Phase $PhaseName
    }
    
    $actionResult.endTime = Get-Date
    $actionResult.executionTime = ($actionResult.endTime - $actionResult.startTime).TotalSeconds
    
    return $actionResult
}

function Execute-Script {
    param(
        [string]$ScriptPath,
        [string]$PhaseName
    )
    
    $scriptResult = @{
        script = Split-Path $ScriptPath -Leaf
        startTime = Get-Date
        endTime = $null
        status = "Running"
        output = @()
        error = $null
        executionTime = 0
    }
    
    try {
        Write-OrchestrationLog "Executing PowerShell script: $($scriptResult.script)" "PROGRESS" -Phase $PhaseName
        
        # Execute script and capture output
        $output = & $ScriptPath 2>&1
        $scriptResult.output = $output
        
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
            throw "Script exited with code: $LASTEXITCODE"
        }
        
        $scriptResult.status = "Completed"
        Write-OrchestrationLog "Script executed successfully" "SUCCESS" -Phase $PhaseName
        
    }
    catch {
        $scriptResult.status = "Failed"
        $scriptResult.error = $_.Exception.Message
        Write-OrchestrationLog "Script execution failed: $($_.Exception.Message)" "ERROR" -Phase $PhaseName
    }
    
    $scriptResult.endTime = Get-Date
    $scriptResult.executionTime = ($scriptResult.endTime - $scriptResult.startTime).TotalSeconds
    
    return $scriptResult
}

function Create-BackupPoint {
    param([string]$PhaseName)
    
    Write-OrchestrationLog "Creating backup point for phase: $PhaseName" "PROGRESS" -Phase $PhaseName
    
    $backupPath = "$ORCHESTRATION_DIR\backups\pre-$PhaseName-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    try {
        # Create backup of templates directory
        if (Test-Path "$UNIFIED_DIR\templates") {
            Copy-Item -Path "$UNIFIED_DIR\templates" -Destination "$backupPath\templates" -Recurse -Force
            Write-OrchestrationLog "Backup created at: $backupPath" "SUCCESS" -Phase $PhaseName
            return $backupPath
        }
        else {
            Write-OrchestrationLog "No templates directory to backup" "INFO" -Phase $PhaseName
            return $null
        }
    }
    catch {
        Write-OrchestrationLog "Backup creation failed: $($_.Exception.Message)" "ERROR" -Phase $PhaseName
        return $null
    }
}

function Generate-ExecutionReport {
    param([array]$PhaseResults)
    
    Write-OrchestrationLog "Generating comprehensive execution report..." "ORCHESTRATION"
    
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        executionSummary = @{
            startTime = $orchestrationStats.startTime
            endTime = $orchestrationStats.endTime
            totalExecutionTime = if($orchestrationStats.endTime -and $orchestrationStats.startTime){($orchestrationStats.endTime - $orchestrationStats.startTime).TotalSeconds}else{0}
            totalPhases = $orchestrationStats.totalPhases
            completedPhases = $orchestrationStats.completedPhases
            failedPhases = $orchestrationStats.failedPhases
            skippedPhases = $orchestrationStats.skippedPhases
            successRate = if($orchestrationStats.totalPhases -gt 0){[math]::Round(($orchestrationStats.completedPhases / $orchestrationStats.totalPhases) * 100, 1)}else{0}
        }
        phaseResults = $PhaseResults
        statistics = @{
            totalComponents = $orchestrationStats.totalComponents
            successfullyProcessed = $orchestrationStats.successfullyProcessed
            errors = $orchestrationStats.errors.Count
            warnings = $orchestrationStats.warnings.Count
        }
        recommendations = @()
        nextSteps = @()
        logs = @{
            masterLog = $MASTER_LOG
            executionReport = $EXECUTION_REPORT
            backupLocation = "$ORCHESTRATION_DIR\backups"
        }
    }
    
    # Generate recommendations based on results
    if ($orchestrationStats.failedPhases -gt 0) {
        $report.recommendations += "$($orchestrationStats.failedPhases) phases failed. Review error logs and re-run failed phases."
    }
    
    if ($orchestrationStats.successRate -lt 90) {
        $report.recommendations += "Success rate is below 90%. Consider investigating root causes of failures."
    }
    
    if ($orchestrationStats.errors.Count -gt 0) {
        $report.recommendations += "$($orchestrationStats.errors.Count) errors occurred. Address these before proceeding."
    }
    
    # Next steps
    $report.nextSteps = @(
        "Review detailed execution logs for any warnings or errors",
        "Validate final template structure using quality assurance framework",
        "Test integration with existing MR.VERMA system",
        "Document any customizations or special configurations",
        "Schedule regular maintenance and optimization runs"
    )
    
    # Save report
    $report | ConvertTo-Json -Depth 5 | Out-File -FilePath $EXECUTION_REPORT -Encoding UTF8
    
    Write-OrchestrationLog "Execution report saved to: $EXECUTION_REPORT" "SUCCESS"
    return $report
}

function Show-OrchestrationDashboard {
    Write-Host "`n=== Template Optimization Orchestration Dashboard ===" -ForegroundColor Cyan
    Write-Host "Project: MR.VERMA Comprehensive Template Optimization" -ForegroundColor White
    Write-Host "Orchestration Directory: $ORCHESTRATION_DIR" -ForegroundColor Gray
    Write-Host "Start Time: $(if($orchestrationStats.startTime){$orchestrationStats.startTime.ToString('yyyy-MM-dd HH:mm:ss')}else{'Not started'})" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📊 Orchestration Statistics:" -ForegroundColor Yellow
    Write-Host "  Total Phases: $($orchestrationStats.totalPhases)" -ForegroundColor White
    Write-Host "  Completed Phases: $($orchestrationStats.completedPhases)" -ForegroundColor Green
    Write-Host "  Failed Phases: $($orchestrationStats.failedPhases)" -ForegroundColor Red
    Write-Host "  Skipped Phases: $($orchestrationStats.skippedPhases)" -ForegroundColor Yellow
    $successRate = if($orchestrationStats.totalPhases -gt 0){[math]::Round(($orchestrationStats.completedPhases / $orchestrationStats.totalPhases) * 100, 1)}else{0}
    $color = if($orchestrationStats.totalPhases -gt 0 -and ($orchestrationStats.completedPhases / $orchestrationStats.totalPhases) -ge 0.9){"Green"}else{"Red"}
    Write-Host "  Success Rate: $successRate%" -ForegroundColor $color
    
    Write-Host "`n🎯 Available Orchestration Modes:" -ForegroundColor Yellow
    Write-Host "  1. Full Optimization (All phases)" -ForegroundColor White
    Write-Host "  2. Analysis Only (Scan and analyze)" -ForegroundColor White
    Write-Host "  3. Installation Only (Install templates)" -ForegroundColor White
    Write-Host "  4. QA Only (Test and validate)" -ForegroundColor White
    Write-Host "  5. Custom (Select specific phases)" -ForegroundColor White
    Write-Host "  6. Status Dashboard" -ForegroundColor White
    
    Write-Host ""
}

function Execute-FullOrchestration {
    param([string]$Mode = "full")
    
    Write-OrchestrationLog "Starting comprehensive template optimization orchestration (Mode: $Mode)" "ORCHESTRATION"
    
    $orchestrationStats.startTime = Get-Date
    $orchestrationStats.totalPhases = $ORCHESTRATION_CONFIG.phases.Count
    
    $phaseResults = @()
    $success = $true
    
    try {
        # Determine which phases to execute based on mode
        $phasesToExecute = switch ($Mode.ToLower()) {
            "full" { $ORCHESTRATION_CONFIG.phases }
            "analysis" { $ORCHESTRATION_CONFIG.phases | Where-Object { $_.name -in @("Pre-Installation Analysis") } }
            "installation" { $ORCHESTRATION_CONFIG.phases | Where-Object { $_.name -in @("Template Installation") } }
            "qa" { $ORCHESTRATION_CONFIG.phases | Where-Object { $_.name -in @("Quality Assurance", "Final Validation") } }
            default { $ORCHESTRATION_CONFIG.phases }
        }
        
        Write-OrchestrationLog "Executing $($phasesToExecute.Count) phases in $Mode mode" "INFO"
        
        # Execute each phase
        $phaseNumber = 1
        foreach ($phase in $phasesToExecute) {
            Write-OrchestrationLog "`n{'='*60}" "INFO"
            Write-OrchestrationLog "PHASE $phaseNumber of $($phasesToExecute.Count): $($phase.name)" "PHASE"
            Write-OrchestrationLog "{'='*60}" "INFO"
            
            # Create backup point if configured
            if ($ORCHESTRATION_CONFIG.options.backupBeforeChanges) {
                $backupPath = Create-BackupPoint -PhaseName $phase.name
                if ($backupPath) {
                    Write-OrchestrationLog "Backup created: $backupPath" "SUCCESS" -Phase $phase.name
                }
            }
            
            # Execute phase
            $phaseResult = Execute-Phase -Phase $phase -PhaseNumber $phaseNumber -TotalPhases $phasesToExecute.Count
            $phaseResults += $phaseResult
            
            # Update statistics
            switch ($phaseResult.status) {
                "Completed" { $orchestrationStats.completedPhases++ }
                "Failed" { 
                    $orchestrationStats.failedPhases++ 
                    if ($phase.critical -and $ORCHESTRATION_CONFIG.options.stopOnCriticalFailure) {
                        $success = $false
                        break
                    }
                }
                "Skipped" { $orchestrationStats.skippedPhases++ }
            }
            
            $phaseNumber++
            
            if (-not $success) {
                break
            }
        }
        
        $orchestrationStats.endTime = Get-Date
        
        # Generate final report
        $executionReport = Generate-ExecutionReport -PhaseResults $phaseResults
        
        Write-OrchestrationLog "`n{'='*60}" "ORCHESTRATION"
        Write-OrchestrationLog "ORCHESTRATION COMPLETED" "ORCHESTRATION"
        Write-OrchestrationLog "{'='*60}" "ORCHESTRATION"
        Write-OrchestrationLog "Total Execution Time: $([math]::Round($executionReport.executionSummary.totalExecutionTime, 1)) seconds" "INFO"
        Write-OrchestrationLog "Success Rate: $($executionReport.executionSummary.successRate)%" $(if($executionReport.executionSummary.successRate -ge 90){"SUCCESS"}else{"WARNING"})
        Write-OrchestrationLog "Phases Completed: $($orchestrationStats.completedPhases)/$($orchestrationStats.totalPhases)" "INFO"
        Write-OrchestrationLog "Report Location: $EXECUTION_REPORT" "INFO"
        Write-OrchestrationLog "Master Log: $MASTER_LOG" "INFO"
        
        return $executionReport
        
    }
    catch {
        $orchestrationStats.endTime = Get-Date
        Write-OrchestrationLog "Orchestration failed: $($_.Exception.Message)" "ERROR"
        
        # Generate partial report
        $executionReport = Generate-ExecutionReport -PhaseResults $phaseResults
        
        return $executionReport
    }
}

function Main {
    param([string]$Mode = "dashboard", [string[]]$CustomPhases = @())
    
    try {
        Initialize-Orchestration
        
        switch ($Mode.ToLower()) {
            "dashboard" { 
                Show-OrchestrationDashboard 
            }
            "full" { 
                $report = Execute-FullOrchestration -Mode "full"
                Write-OrchestrationLog "Full orchestration completed. Report generated with $($report.executionSummary.successRate)% success rate" "SUCCESS"
                return $report
            }
            "analysis" { 
                $report = Execute-FullOrchestration -Mode "analysis"
                Write-OrchestrationLog "Analysis phase completed" "SUCCESS"
                return $report
            }
            "installation" { 
                $report = Execute-FullOrchestration -Mode "installation"
                Write-OrchestrationLog "Installation phase completed" "SUCCESS"
                return $report
            }
            "qa" { 
                $report = Execute-FullOrchestration -Mode "qa"
                Write-OrchestrationLog "QA phase completed" "SUCCESS"
                return $report
            }
            "custom" { 
                if ($CustomPhases.Count -gt 0) {
                    Write-OrchestrationLog "Executing custom phases: $($CustomPhases -join ', ')" "INFO"
                    # Implement custom phase execution
                    Write-OrchestrationLog "Custom phase execution not yet implemented" "WARNING"
                }
                else {
                    Write-OrchestrationLog "No custom phases specified" "ERROR"
                }
            }
            default { 
                Write-OrchestrationLog "Unknown mode: $Mode" "ERROR"
                Show-OrchestrationDashboard
            }
        }
    }
    catch {
        Write-OrchestrationLog "Critical orchestration error: $($_.Exception.Message)" "ERROR"
        Write-OrchestrationLog "Stack trace: $($_.ScriptStackTrace)" "ERROR"
        return $null
    }
}

# Execute based on parameters
if ($args.Count -gt 0) {
    $mode = $args[0]
    $customPhases = if($args.Count -gt 1){$args[1..($args.Count-1)]}else{@()}
    
    Main -Mode $mode -CustomPhases $customPhases
}
else {
    Main -Mode "dashboard"
}