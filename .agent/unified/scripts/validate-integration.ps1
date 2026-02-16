# 🧪 Claude Code Integration Validation Script
# Validates all installed templates and configurations

$ErrorActionPreference = "Stop"

Write-Host "Starting Claude Code Integration Validation..." -ForegroundColor Green

# Configuration
$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$CONFIG_DIR = "$PROJECT_ROOT\.agent\unified\config"
$TEMPLATES_DIR = "$PROJECT_ROOT\.agent\unified\templates"
$LOG_FILE = "$CONFIG_DIR\validation.log"

# Validation results
$validationResults = @{
    total = 0
    passed = 0
    failed = 0
    errors = @()
}

function Write-Log {
    param($Message, $Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Type] $Message"
    
    switch ($Type) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry -ForegroundColor Cyan }
    }
    
    Add-Content -Path $LOG_FILE -Value $logEntry
}

function Test-FileExists {
    param($FilePath, $ComponentType, $ComponentName)
    
    $validationResults.total++
    
    if (Test-Path $FilePath) {
        Write-Log "$ComponentType '$ComponentName' - File exists: $FilePath" "SUCCESS"
        $validationResults.passed++
        return $true
    } else {
        Write-Log "$ComponentType '$ComponentName' - File missing: $FilePath" "ERROR"
        $validationResults.failed++
        $validationResults.errors += "Missing file: $FilePath"
        return $false
    }
}

function Test-JsonValid {
    param($FilePath, $ComponentType, $ComponentName)
    
    try {
        $jsonContent = Get-Content $FilePath -Raw
        $null = $jsonContent | ConvertFrom-Json
        Write-Log "$ComponentType '$ComponentName' - JSON valid" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "$ComponentType '$ComponentName' - JSON invalid: $($_.Exception.Message)" "ERROR"
        $validationResults.errors += "Invalid JSON in: $FilePath - $($_.Exception.Message)"
        return $false
    }
}

function Test-TemplateStructure {
    param($TemplatePath, $ComponentType, $ComponentName)
    
    $requiredFiles = @()
    
    switch ($ComponentType) {
        "Agent" {
            $requiredFiles = @("agent.json", "template.md")
        }
        "Command" {
            $requiredFiles = @("command.json", "implementation.js")
        }
        "Setting" {
            $requiredFiles = @("setting.json")
        }
        "Hook" {
            $requiredFiles = @("hook.json", "hook.js")
        }
        "MCP" {
            $requiredFiles = @("mcp.json")
        }
        "Skill" {
            $requiredFiles = @("skill.json", "implementation.py")
        }
    }
    
    $allValid = $true
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $TemplatePath $file
        if (-not (Test-FileExists $filePath $ComponentType "$ComponentName/$file")) {
            $allValid = $false
        }
    }
    
    return $allValid
}

function Validate-Agents {
    Write-Host "Validating Agents..." -ForegroundColor Yellow
    
    $agents = @(
        "development-tools/tooling-engineer",
        "security/powershell-security-hardening",
        "programming-languages/powershell-ui-architect",
        "development-tools/command-expert",
        "data-ai/machine-learning-engineer",
        "development-team/electron-pro",
        "development-team/mobile-app-developer",
        "development-team/mobile-developer",
        "development-tools/debugger",
        "development-tools/performance-engineer",
        "development-tools/performance-profiler",
        "expert-advisors/agent-organizer",
        "expert-advisors/context-manager",
        "expert-advisors/performance-monitor",
        "expert-advisors/task-distributor",
        "expert-advisors/voidbeast-gpt41enhanced",
        "performance-testing/react-performance-optimization",
        "programming-languages/c-pro",
        "programming-languages/cpp-pro",
        "programming-languages/csharp-developer",
        "programming-languages/elixir-expert",
        "programming-languages/embedded-systems",
        "programming-languages/flutter-expert",
        "programming-languages/golang-pro",
        "programming-languages/javascript-pro",
        "programming-languages/rust-engineer",
        "programming-languages/rust-pro",
        "realtime/websocket-engineer",
        "programming-languages/swift-expert"
    )
    
    foreach ($agent in $agents) {
        $agentPath = Join-Path $TEMPLATES_DIR "agents\$agent"
        if (Test-TemplateStructure $agentPath "Agent" $agent) {
            $agentJsonPath = Join-Path $agentPath "agent.json"
            Test-JsonValid $agentJsonPath "Agent" $agent
        }
    }
}

function Validate-Commands {
    Write-Host "Validating Commands..." -ForegroundColor Yellow
    
    $commands = @(
        "automation/workflow-orchestrator",
        "deployment/changelog-demo-command",
        "team/memory-spring-cleaning",
        "performance/optimize-memory-usage",
        "team/session-learning-capture"
    )
    
    foreach ($command in $commands) {
        $commandPath = Join-Path $TEMPLATES_DIR "commands\$command"
        if (Test-TemplateStructure $commandPath "Command" $command) {
            $commandJsonPath = Join-Path $commandPath "command.json"
            Test-JsonValid $commandJsonPath "Command" $command
        }
    }
}

function Validate-Settings {
    Write-Host "Validating Settings..." -ForegroundColor Yellow
    
    $settings = @(
        "statusline/vercel-multi-env-status",
        "statusline/command-statusline",
        "statusline/game-performance-monitor-statusline",
        "statusline/unity-project-dashboard-statusline"
    )
    
    foreach ($setting in $settings) {
        $settingPath = Join-Path $TEMPLATES_DIR "settings\$setting"
        if (Test-TemplateStructure $settingPath "Setting" $setting) {
            $settingJsonPath = Join-Path $settingPath "setting.json"
            Test-JsonValid $settingJsonPath "Setting" $setting
        }
    }
}

function Validate-Hooks {
    Write-Host "Validating Hooks..." -ForegroundColor Yellow
    
    $hooks = @(
        "post-tool/format-python-files",
        "testing/test-runner",
        "development-tools/command-logger",
        "performance/performance-monitor"
    )
    
    foreach ($hook in $hooks) {
        $hookPath = Join-Path $TEMPLATES_DIR "hooks\$hook"
        if (Test-TemplateStructure $hookPath "Hook" $hook) {
            $hookJsonPath = Join-Path $hookPath "hook.json"
            Test-JsonValid $hookJsonPath "Hook" $hook
        }
    }
}

function Validate-MCPs {
    Write-Host "Validating MCPs..." -ForegroundColor Yellow
    
    $mcps = @(
        "integration/memory-integration"
    )
    
    foreach ($mcp in $mcps) {
        $mcpPath = Join-Path $TEMPLATES_DIR "mcp\$mcp"
        if (Test-TemplateStructure $mcpPath "MCP" $mcp) {
            $mcpJsonPath = Join-Path $mcpPath "mcp.json"
            Test-JsonValid $mcpJsonPath "MCP" $mcp
        }
    }
}

function Validate-Skills {
    Write-Host "Validating Skills..." -ForegroundColor Yellow
    
    $skills = @(
        "ai-research/agent-memory-mcp",
        "ai-research/agent-memory-systems",
        "ai-research/agents-crewai",
        "ai-research/agents-langchain",
        "ai-research/fine-tuning-peft",
        "ai-research/optimization-hqq",
        "ai-research/optimization-gptq",
        "ai-research/optimization-flash-attention",
        "ai-research/optimization-bitsandbytes",
        "ai-research/fine-tuning-unsloth",
        "ai-research/tokenization-sentencepiece",
        "ai-research/inference-serving-vllm",
        "ai-research/inference-serving-llama-cpp",
        "ai-research/crewai",
        "ai-research/ai-agents-architect",
        "scientific/vaex",
        "scientific/get-available-resources",
        "enterprise-communication/session-handoff",
        "railway/metrics"
    )
    
    foreach ($skill in $skills) {
        $skillPath = Join-Path $TEMPLATES_DIR "skills\$skill"
        if (Test-TemplateStructure $skillPath "Skill" $skill) {
            $skillJsonPath = Join-Path $skillPath "skill.json"
            Test-JsonValid $skillJsonPath "Skill" $skill
        }
    }
}

function Validate-ConfigurationFiles {
    Write-Host "Validating Configuration Files..." -ForegroundColor Yellow
    
    $configFiles = @(
        "claude-code-integration.md",
        "claude-code-config.json"
    )
    
    foreach ($configFile in $configFiles) {
        $configPath = Join-Path $CONFIG_DIR $configFile
        if (Test-FileExists $configPath "Configuration" $configFile) {
            if ($configFile.EndsWith(".json")) {
                Test-JsonValid $configPath "Configuration" $configFile
            }
        }
    }
}

function Validate-DirectoryStructure {
    Write-Host "Validating Directory Structure..." -ForegroundColor Yellow
    
    $requiredDirs = @(
        "agents",
        "commands", 
        "settings",
        "hooks",
        "mcp",
        "skills"
    )
    
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $TEMPLATES_DIR $dir
        if (Test-Path $dirPath) {
            Write-Log "Directory '$dir' exists" "SUCCESS"
            $validationResults.passed++
        } else {
            Write-Log "Directory '$dir' missing" "ERROR"
            $validationResults.failed++
            $validationResults.errors += "Missing directory: $dirPath"
        }
        $validationResults.total++
    }
}

function Show-ValidationSummary {
    Write-Host "`nValidation Summary" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    Write-Host "Total Tests: $($validationResults.total)" -ForegroundColor White
    Write-Host "Passed: $($validationResults.passed)" -ForegroundColor Green
    Write-Host "Failed: $($validationResults.failed)" -ForegroundColor Red
    
    if ($validationResults.failed -gt 0) {
        Write-Host "`nErrors Found:" -ForegroundColor Red
        foreach ($error in $validationResults.errors) {
            Write-Host "  - $error" -ForegroundColor Red
        }
        return $false
    } else {
        Write-Host "`nAll validations passed!" -ForegroundColor Green
        return $true
    }
}

# Main validation process
function Main {
    Write-Log "Starting comprehensive validation..."
    
    # Validate directory structure first
    Validate-DirectoryStructure
    
    # Validate all components
    Validate-Agents
    Validate-Commands
    Validate-Settings
    Validate-Hooks
    Validate-MCPs
    Validate-Skills
    Validate-ConfigurationFiles
    
    # Show summary
    $success = Show-ValidationSummary
    
    if ($success) {
        Write-Log "Validation completed successfully!" "SUCCESS"
        exit 0
    } else {
        Write-Log "Validation failed with errors!" "ERROR"
        exit 1
    }
}

# Run main function
Main