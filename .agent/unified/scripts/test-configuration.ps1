# 🧪 Claude Code Configuration Testing Script
# Tests all configurations and integrations

$ErrorActionPreference = "Stop"

Write-Host "🧪 Starting Claude Code Configuration Testing..." -ForegroundColor Green

# Configuration
$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$CONFIG_DIR = "$PROJECT_ROOT\.agent\unified\config"
$TEMPLATES_DIR = "$PROJECT_ROOT\.agent\unified\templates"
$LOG_FILE = "$CONFIG_DIR\testing.log"

# Test results
$testResults = @{
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

function Test-ConfigurationFile {
    param($ConfigPath, $TestName)
    
    $testResults.total++
    
    try {
        Write-Log "Testing: $TestName"
        
        if (-not (Test-Path $ConfigPath)) {
            throw "Configuration file not found: $ConfigPath"
        }
        
        $configContent = Get-Content $ConfigPath -Raw | ConvertFrom-Json
        
        # Test basic structure
        if (-not $configContent.version) {
            throw "Missing version field"
        }
        
        if (-not $configContent.name) {
            throw "Missing name field"
        }
        
        Write-Log "✅ $TestName - Configuration structure valid" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ $TestName - Configuration test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "$TestName failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-AgentConfiguration {
    param($AgentPath)
    
    $testResults.total++
    
    try {
        $agentConfig = Get-Content "$TEMPLATES_DIR\agents\$AgentPath\agent.json" -Raw | ConvertFrom-Json
        
        # Test required fields
        $requiredFields = @("name", "version", "description", "type", "enabled", "config")
        foreach ($field in $requiredFields) {
            if (-not $agentConfig.$field) {
                throw "Missing required field: $field"
            }
        }
        
        # Test integration settings
        if (-not $agentConfig.integration.claude_code -or -not $agentConfig.integration.mr_verma) {
            throw "Missing integration settings"
        }
        
        Write-Log "✅ Agent '$AgentPath' - Configuration valid" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ Agent '$AgentPath' - Configuration test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "Agent '$AgentPath' failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-CommandConfiguration {
    param($CommandPath)
    
    $testResults.total++
    
    try {
        $commandConfig = Get-Content "$TEMPLATES_DIR\commands\$CommandPath\command.json" -Raw | ConvertFrom-Json
        
        # Test required fields
        $requiredFields = @("name", "version", "description", "type", "enabled", "config")
        foreach ($field in $requiredFields) {
            if (-not $commandConfig.$field) {
                throw "Missing required field: $field"
            }
        }
        
        # Test implementation file exists
        $implementationPath = "$TEMPLATES_DIR\commands\$CommandPath\implementation.js"
        if (-not (Test-Path $implementationPath)) {
            throw "Missing implementation file: $implementationPath"
        }
        
        Write-Log "✅ Command '$CommandPath' - Configuration valid" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ Command '$CommandPath' - Configuration test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "Command '$CommandPath' failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-SkillConfiguration {
    param($SkillPath)
    
    $testResults.total++
    
    try {
        $skillConfig = Get-Content "$TEMPLATES_DIR\skills\$SkillPath\skill.json" -Raw | ConvertFrom-Json
        
        # Test required fields
        $requiredFields = @("name", "version", "description", "type", "enabled", "config")
        foreach ($field in $requiredFields) {
            if (-not $skillConfig.$field) {
                throw "Missing required field: $field"
            }
        }
        
        # Test implementation file exists
        $implementationPath = "$TEMPLATES_DIR\skills\$SkillPath\implementation.py"
        if (-not (Test-Path $implementationPath)) {
            throw "Missing implementation file: $implementationPath"
        }
        
        Write-Log "✅ Skill '$SkillPath' - Configuration valid" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ Skill '$SkillPath' - Configuration test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "Skill '$SkillPath' failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-IntegrationCompatibility {
    Write-Log "Testing integration compatibility..."
    
    $testResults.total++
    
    try {
        # Test main configuration
        $mainConfig = Get-Content "$CONFIG_DIR\claude-code-config.json" -Raw | ConvertFrom-Json
        
        # Test agents compatibility
        $agents = @(
            "development-tools/tooling-engineer",
            "security/powershell-security-hardening",
            "programming-languages/powershell-ui-architect"
        )
        
        foreach ($agent in $agents) {
            $agentConfigPath = "$TEMPLATES_DIR\agents\$agent\agent.json"
            if (Test-Path $agentConfigPath) {
                $agentConfig = Get-Content $agentConfigPath -Raw | ConvertFrom-Json
                if (-not $agentConfig.integration.claude_code -or -not $agentConfig.integration.mr_verma) {
                    throw "Agent '$agent' missing integration settings"
                }
            }
        }
        
        Write-Log "✅ Integration compatibility test passed" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ Integration compatibility test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "Integration compatibility failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-ConfigurationIntegrity {
    Write-Log "Testing configuration integrity..."
    
    $testResults.total++
    
    try {
        # Load main configuration
        $mainConfig = Get-Content "$CONFIG_DIR\claude-code-config.json" -Raw | ConvertFrom-Json
        
        # Test version consistency
        if ($mainConfig.version -ne "2.0") {
            throw "Invalid main configuration version: $($mainConfig.version)"
        }
        
        # Test component references
        $totalComponents = 0
        $validComponents = 0
        
        # Test agents
        foreach ($agent in $mainConfig.agents.PSObject.Properties) {
            $totalComponents++
            $agentPath = $agent.Name
            $agentConfigPath = "$TEMPLATES_DIR\agents\$agentPath\agent.json"
            
            if (Test-Path $agentConfigPath) {
                $validComponents++
            } else {
                Write-Log "⚠️ Agent '$agentPath' referenced but template missing" "WARNING"
            }
        }
        
        # Test commands
        foreach ($command in $mainConfig.commands.PSObject.Properties) {
            $totalComponents++
            $commandPath = $command.Name
            $commandConfigPath = "$TEMPLATES_DIR\commands\$commandPath\command.json"
            
            if (Test-Path $commandConfigPath) {
                $validComponents++
            } else {
                Write-Log "⚠️ Command '$commandPath' referenced but template missing" "WARNING"
            }
        }
        
        # Test skills
        foreach ($skill in $mainConfig.skills.PSObject.Properties) {
            $totalComponents++
            $skillPath = $skill.Name
            $skillConfigPath = "$TEMPLATES_DIR\skills\$skillPath\skill.json"
            
            if (Test-Path $skillConfigPath) {
                $validComponents++
            } else {
                Write-Log "⚠️ Skill '$skillPath' referenced but template missing" "WARNING"
            }
        }
        
        Write-Log "✅ Configuration integrity test passed ($validComponents/$totalComponents components valid)" "SUCCESS"
        $testResults.passed++
        return $true
    }
    catch {
        Write-Log "❌ Configuration integrity test failed: $($_.Exception.Message)" "ERROR"
        $testResults.failed++
        $testResults.errors += "Configuration integrity failed: $($_.Exception.Message)"
        return $false
    }
}

function Show-TestSummary {
    Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    Write-Host "Total Tests: $($testResults.total)" -ForegroundColor White
    Write-Host "Passed: $($testResults.passed)" -ForegroundColor Green
    Write-Host "Failed: $($testResults.failed)" -ForegroundColor Red
    
    if ($testResults.failed -gt 0) {
        Write-Host "`n❌ Test Failures:" -ForegroundColor Red
        foreach ($error in $testResults.errors) {
            Write-Host "  - $error" -ForegroundColor Red
        }
        return $false
    } else {
        Write-Host "`n✅ All tests passed!" -ForegroundColor Green
        return $true
    }
}

# Main testing process
function Main {
    Write-Log "🧪 Starting comprehensive configuration testing..."
    
    # Test main configuration files
    Test-ConfigurationFile "$CONFIG_DIR\claude-code-config.json" "Main Configuration"
    Test-ConfigurationFile "$CONFIG_DIR\claude-code-integration.md" "Integration Documentation"
    
    # Test agent configurations
    $agents = @(
        "development-tools/tooling-engineer",
        "security/powershell-security-hardening",
        "programming-languages/powershell-ui-architect"
    )
    
    foreach ($agent in $agents) {
        Test-AgentConfiguration $agent
    }
    
    # Test command configurations
    $commands = @(
        "automation/workflow-orchestrator",
        "deployment/changelog-demo-command"
    )
    
    foreach ($command in $commands) {
        Test-CommandConfiguration $command
    }
    
    # Test skill configurations
    $skills = @(
        "ai-research/agent-memory-mcp",
        "ai-research/agents-crewai",
        "scientific/vaex"
    )
    
    foreach ($skill in $skills) {
        Test-SkillConfiguration $skill
    }
    
    # Test integration compatibility
    Test-IntegrationCompatibility
    
    # Test configuration integrity
    Test-ConfigurationIntegrity
    
    # Show summary
    $success = Show-TestSummary
    
    if ($success) {
        Write-Log "🎉 Configuration testing completed successfully!" "SUCCESS"
        exit 0
    } else {
        Write-Log "❌ Configuration testing failed with errors!" "ERROR"
        exit 1
    }
}

# Run main function
Main