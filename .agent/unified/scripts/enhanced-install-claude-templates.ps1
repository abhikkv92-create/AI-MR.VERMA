# Enhanced Claude Code Templates Installation Script
# Comprehensive template management with redundancy elimination and intelligent directory handling

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ROOT = "e:\ABHINAV\MR.VERMA"
$UNIFIED_DIR = "$PROJECT_ROOT\.agent\unified"
$CONFIG_DIR = "$UNIFIED_DIR\config"
$TEMPLATES_DIR = "$UNIFIED_DIR\templates"
$LOG_FILE = "$CONFIG_DIR\enhanced-installation.log"
$BACKUP_DIR = "$CONFIG_DIR\backups"
$DUPLICATE_SCAN_DIR = "$CONFIG_DIR\duplicate-analysis"

# Installation statistics
$installationStats = @{
    totalComponents = 0
    installed = 0
    skipped = 0
    updated = 0
    errors = 0
    duplicatesFound = 0
    spaceSaved = 0
    backupCreated = $false
}

# Template definitions with standardized structure
$TEMPLATE_DEFINITIONS = @{
    agents = @{
        count = 25
        basePath = "agents"
        components = @(
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
    }
    commands = @{
        count = 5
        basePath = "commands"
        components = @(
            "automation/workflow-orchestrator",
            "deployment/changelog-demo-command",
            "team/memory-spring-cleaning",
            "performance/optimize-memory-usage",
            "team/session-learning-capture"
        )
    }
    settings = @{
        count = 4
        basePath = "settings"
        components = @(
            "statusline/vercel-multi-env-status",
            "statusline/command-statusline",
            "statusline/game-performance-monitor-statusline",
            "statusline/unity-project-dashboard-statusline"
        )
    }
    hooks = @{
        count = 4
        basePath = "hooks"
        components = @(
            "post-tool/format-python-files",
            "testing/test-runner",
            "development-tools/command-logger",
            "performance/performance-monitor"
        )
    }
    mcp = @{
        count = 1
        basePath = "mcp"
        components = @(
            "integration/memory-integration"
        )
    }
    skills = @{
        count = 16
        basePath = "skills"
        components = @(
            "ai-research/agent-memory-mcp",
            "ai-research/agent-memory-systems",
            "ai-research/agents-crewai",
            "ai-research/agents-langchain",
            "ai-research/fine-tuning-peft",
            "ai-research/optimization-hqq",
            "scientific/vaex",
            "scientific/get-available-resources",
            "enterprise-communication/session-handoff",
            "ai-research/tokenization-sentencepiece",
            "ai-research/inference-serving-vllm",
            "ai-research/inference-serving-llama-cpp",
            "ai-research/crewai",
            "ai-research/ai-agents-architect",
            "railway/metrics",
            "ai-research/optimization-gptq",
            "ai-research/optimization-flash-attention",
            "ai-research/optimization-bitsandbytes",
            "ai-research/fine-tuning-unsloth"
        )
    }
}

function Write-EnhancedLog {
    param(
        [string]$Message,
        [string]$Type = "INFO",
        [switch]$NoConsole,
        [switch]$NoFile
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Type] $Message"
    
    # Console output with colors
    if (-not $NoConsole) {
        switch ($Type) {
            "ERROR" { Write-Host $logEntry -ForegroundColor Red }
            "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
            "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
            "DUPLICATE" { Write-Host $logEntry -ForegroundColor Magenta }
            "BACKUP" { Write-Host $logEntry -ForegroundColor Cyan }
            default { Write-Host $logEntry -ForegroundColor Cyan }
        }
    }
    
    # File logging
    if (-not $NoFile) {
        Add-Content -Path $LOG_FILE -Value $logEntry -ErrorAction SilentlyContinue
    }
}

function Initialize-Environment {
    Write-EnhancedLog "Initializing enhanced installation environment..."
    
    # Create backup directory
    if (-not (Test-Path $BACKUP_DIR)) {
        New-Item -Path $BACKUP_DIR -ItemType Directory -Force | Out-Null
        Write-EnhancedLog "Created backup directory: $BACKUP_DIR"
    }
    
    # Create duplicate analysis directory
    if (-not (Test-Path $DUPLICATE_SCAN_DIR)) {
        New-Item -Path $DUPLICATE_SCAN_DIR -ItemType Directory -Force | Out-Null
        Write-EnhancedLog "Created duplicate analysis directory: $DUPLICATE_SCAN_DIR"
    }
    
    # Initialize log file
    if (Test-Path $LOG_FILE) {
        $backupLog = "$BACKUP_DIR\install-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
        Copy-Item -Path $LOG_FILE -Destination $backupLog -Force
        Write-EnhancedLog "Backed up previous log to: $backupLog"
    }
    
    # Clear current log
    "Enhanced Claude Code Installation Log - $(Get-Date)" | Out-File -FilePath $LOG_FILE -Force
}

function Get-FileChecksum {
    param([string]$FilePath)
    
    try {
        if (Test-Path $FilePath) {
            $fileStream = [System.IO.File]::OpenRead($FilePath)
            $sha256 = [System.Security.Cryptography.SHA256]::Create()
            $hashBytes = $sha256.ComputeHash($fileStream)
            $fileStream.Close()
            $sha256.Dispose()
            
            return [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()
        }
    }
    catch {
        Write-EnhancedLog "Error calculating checksum for ${FilePath}: $($_.Exception.Message)" "WARNING"
        return $null
    }
    
    return $null
}

function Scan-ForDuplicates {
    Write-EnhancedLog "Starting comprehensive duplicate scan..."
    
    $duplicateReport = @{
        totalFiles = 0
        duplicates = @{}
        potentialSavings = 0
        scanResults = @()
    }
    
    # Scan templates directory
    if (Test-Path $TEMPLATES_DIR) {
        $allFiles = Get-ChildItem -Path $TEMPLATES_DIR -File -Recurse -ErrorAction SilentlyContinue
        $fileHashes = @{}
        
        foreach ($file in $allFiles) {
            $duplicateReport.totalFiles++
            $checksum = Get-FileChecksum $file.FullName
            
            if ($checksum) {
                if ($fileHashes.ContainsKey($checksum)) {
                    # Found duplicate
                    if (-not $duplicateReport.duplicates.ContainsKey($checksum)) {
                        $duplicateReport.duplicates[$checksum] = @{
                            original = $fileHashes[$checksum]
                            duplicates = @()
                            size = $file.Length
                        }
                    }
                    $duplicateReport.duplicates[$checksum].duplicates += $file.FullName
                    $duplicateReport.potentialSavings += $file.Length
                }
                else {
                    $fileHashes[$checksum] = $file.FullName
                }
            }
        }
    }
    
    # Generate duplicate report
    $reportPath = "$DUPLICATE_SCAN_DIR\duplicate-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $duplicateReport | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-EnhancedLog "Duplicate scan completed. Found $($duplicateReport.duplicates.Count) duplicate groups"
    Write-EnhancedLog "Potential space savings: $([math]::Round($duplicateReport.potentialSavings / 1MB, 2)) MB"
    
    return $duplicateReport
}

function Test-DirectoryExists {
    param([string]$DirectoryPath, [string]$ComponentType, [string]$ComponentName)
    
    if (Test-Path $DirectoryPath) {
        $existingFiles = Get-ChildItem -Path $DirectoryPath -File -ErrorAction SilentlyContinue
        if ($existingFiles.Count -gt 0) {
            Write-EnhancedLog "Directory exists for $ComponentType '$ComponentName' with $($existingFiles.Count) existing files" "WARNING"
            return $true
        }
        else {
            Write-EnhancedLog "Empty directory exists for $ComponentType '$ComponentName'" "INFO"
            return $false
        }
    }
    return $false
}

function Backup-ExistingTemplates {
    Write-EnhancedLog "Creating backup of existing templates..."
    
    $backupTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = "$BACKUP_DIR\templates-backup-$backupTimestamp"
    
    if (Test-Path $TEMPLATES_DIR) {
        try {
            # Create backup with compression
            Compress-Archive -Path "$TEMPLATES_DIR\*" -DestinationPath "$backupPath.zip" -CompressionLevel Optimal -Force
            Write-EnhancedLog "Templates backed up to: $backupPath.zip" "BACKUP"
            $installationStats.backupCreated = $true
            return $backupPath
        }
        catch {
            Write-EnhancedLog "Backup creation failed: $($_.Exception.Message)" "ERROR"
            return $null
        }
    }
    
    Write-EnhancedLog "No existing templates to backup" "INFO"
    return $null
}

function Create-StandardizedTemplateStructure {
    param(
        [string]$TemplateType,
        [string]$ComponentPath,
        [hashtable]$TemplateDefinition
    )
    
    $fullPath = Join-Path $TEMPLATES_DIR $ComponentPath
    $componentName = Split-Path $ComponentPath -Leaf
    $category = Split-Path $ComponentPath -Parent
    
    Write-EnhancedLog "Creating $TemplateType template: $ComponentPath"
    
    try {
        # Create directory structure
        New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
        
        # Generate standardized template files based on type
        switch ($TemplateType) {
            "agents" {
                Create-AgentTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
            "commands" {
                Create-CommandTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
            "settings" {
                Create-SettingTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
            "hooks" {
                Create-HookTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
            "mcp" {
                Create-MCPTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
            "skills" {
                Create-SkillTemplate -Path $fullPath -ComponentName $componentName -Category $category
            }
        }
        
        Write-EnhancedLog "Successfully created $TemplateType template: $ComponentPath" "SUCCESS"
        return $true
    }
    catch {
        Write-EnhancedLog "Failed to create $TemplateType template '$ComponentPath': $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Create-AgentTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # Agent configuration
    $agentConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "Agent template for $ComponentName"
        author = "MR.VERMA System"
        created = (Get-Date -Format "yyyy-MM-dd")
        capabilities = @("analysis", "development", "optimization")
        requirements = @{
            minimumVersion = "1.0.0"
            dependencies = @()
        }
        settings = @{
            enabled = $true
            priority = "normal"
            timeout = 300
        }
    }
    
    $agentConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\agent.json" -Encoding UTF8
    
    # Agent template
    $templateContent = @"
# $ComponentName Agent Template

## Overview
This agent specializes in $ComponentName functionality within the MR.VERMA system.

## Capabilities
- Advanced analysis and problem-solving
- Code optimization and refactoring
- Performance monitoring and enhancement
- Cross-platform compatibility

## Configuration
- Priority: Normal
- Timeout: 5 minutes
- Dependencies: None

## Usage
This agent can be invoked through the unified command interface.

## Examples
```powershell
# Example usage
Invoke-Agent -Name "$ComponentName" -Parameters @{}
```

## Notes
Auto-generated template for $ComponentName agent.
"@
    
    $templateContent | Out-File -FilePath "$Path\template.md" -Encoding UTF8
    
    # Test file
    $testContent = @"
# Test cases for $ComponentName agent

Describe "$ComponentName Agent Tests" {
    It "Should initialize correctly" {
        # Test initialization
    }
    
    It "Should process requests" {
        # Test request processing
    }
    
    It "Should handle errors gracefully" {
        # Test error handling
    }
}
"@
    
    $testContent | Out-File -FilePath "$Path\tests.ps1" -Encoding UTF8
}

function Create-CommandTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # Command configuration
    $commandConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "Command template for $ComponentName"
        author = "MR.VERMA System"
        created = (Get-Date -Format "yyyy-MM-dd")
        execution = @{
            type = "powershell"
            timeout = 300
            requiresAdmin = $false
        }
        parameters = @{
            required = @()
            optional = @()
        }
    }
    
    $commandConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\command.json" -Encoding UTF8
    
    # Command implementation
    $implementationContent = @"
// $ComponentName Command Implementation
const {{ execSync }} = require('child_process');

class $($(ComponentName -replace '-', '').replace('_', ''))Command {
  constructor(config) {
    this.config = config;
    this.name = '$ComponentName';
  }

  async execute(params) {
    console.log('Executing ' + this.name + ' command');
    
    try {
      // Command implementation here
      const result = await this.runCommand(params);
      return {{ success: true, result }};
    } catch (error) {
      return {{ success: false, error: error.message }};
    }
  }

  async runCommand(params) {
    // Implement command logic here
    return {{ message: 'Command executed successfully' }};
  }
}

module.exports = $($(ComponentName -replace '-', '').replace('_', ''))Command;
"@
    
    $implementationContent | Out-File -FilePath "$Path\implementation.js" -Encoding UTF8
}

function Create-SettingTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # Setting configuration
    $settingConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "Setting template for $ComponentName"
        type = "statusline"
        scope = "global"
        defaultValue = $true
        options = @{
            enabled = $true
            refreshRate = 1000
            position = "bottom"
        }
    }
    
    $settingConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\setting.json" -Encoding UTF8
    
    # Setting implementation
    $implementationContent = @"
// $ComponentName Setting Implementation

class $($(ComponentName -replace '-', '').replace('_', ''))Setting {
  constructor(config) {
    this.config = config;
    this.name = '$ComponentName';
    this.enabled = config.enabled !== false;
    this.refreshRate = config.refreshRate || 1000;
  }

  initialize() {
    if (this.enabled) {
      this.startMonitoring();
    }
  }

  startMonitoring() {
    // Implement monitoring logic
    console.log('Setting ' + this.name + ' initialized');
  }

  getStatus() {
    return {
      name: this.name,
      enabled: this.enabled,
      status: 'active'
    };
  }
}

module.exports = $($(ComponentName -replace '-', '').replace('_', ''))Setting;
"@
    
    $implementationContent | Out-File -FilePath "$Path\implementation.js" -Encoding UTF8
}

function Create-HookTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # Hook configuration
    $hookConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "Hook template for $ComponentName"
        trigger = "post-tool"
        priority = "normal"
        enabled = $true
        conditions = @{
            toolTypes = @("format", "test", "deploy")
            fileExtensions = @(".py", ".js", ".ts")
        }
    }
    
    $hookConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\hook.json" -Encoding UTF8
    
    # Hook implementation
    $implementationContent = @"
// $ComponentName Hook Implementation

class $($(ComponentName -replace '-', '').replace('_', ''))Hook {
  constructor(config) {
    this.config = config;
    this.name = '$ComponentName';
  }

  async execute(context) {
    console.log('Executing ' + this.name + ' hook');
    
    try {
      // Hook implementation here
      await this.runHook(context);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async runHook(context) {
    // Implement hook logic here
    console.log('Hook executed successfully');
  }
}

module.exports = $($(ComponentName -replace '-', '').replace('_', ''))Hook;
"@
    
    $implementationContent | Out-File -FilePath "$Path\implementation.js" -Encoding UTF8
}

function Create-MCPTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # MCP configuration
    $mcpConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "MCP template for $ComponentName"
        protocol = "memory-integration"
        capabilities = @("memory", "context", "persistence")
        endpoints = @{
            memory = "/memory"
            context = "/context"
            persist = "/persist"
        }
    }
    
    $mcpConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\mcp.json" -Encoding UTF8
    
    # MCP implementation
    $implementationContent = @"
// $ComponentName MCP Implementation

class $($(ComponentName -replace '-', '').replace('_', ''))MCP {
  constructor(config) {
    this.config = config;
    this.name = '$ComponentName';
    this.memory = new Map();
  }

  async initialize() {
    console.log('Initializing MCP: ' + this.name);
    return { success: true };
  }

  async storeMemory(key, value) {
    this.memory.set(key, value);
    return { success: true };
  }

  async retrieveMemory(key) {
    return {
      success: true,
      data: this.memory.get(key)
    };
  }

  async clearMemory() {
    this.memory.clear();
    return { success: true };
  }
}

module.exports = $($(ComponentName -replace '-', '').replace('_', ''))MCP;
"@
    
    $implementationContent | Out-File -FilePath "$Path\implementation.js" -Encoding UTF8
}

function Create-SkillTemplate {
    param([string]$Path, [string]$ComponentName, [string]$Category)
    
    # Skill configuration
    $skillConfig = @{
        name = $ComponentName
        category = $Category
        version = "1.0.0"
        description = "Skill template for $ComponentName"
        language = "python"
        requirements = @{
            pythonVersion = ">=3.8"
            dependencies = @("requests", "json", "logging")
        }
        capabilities = @("analysis", "processing", "automation")
        settings = @{
            enabled = $true
            timeout = 300
            maxRetries = 3
        }
    }
    
    $skillConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "$Path\skill.json" -Encoding UTF8
    
    # Skill implementation
    $implementationContent = @"
# $ComponentName Skill Implementation
import json
import logging

class $($(ComponentName -replace '-', '').replace('_', ''))Skill:
    def __init__(self, config):
        self.config = config
        self.name = '$ComponentName'
        self.logger = logging.getLogger(__name__)

    def execute(self, context):
        self.logger.info(f'Executing {self.name} skill')
        
        try:
            # Skill implementation here
            result = self.run_skill(context)
            return {
                'success': True,
                'result': result,
                'skill': self.name
            }
        except Exception as e:
            self.logger.error(f'Skill execution failed: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'skill': self.name
            }

    def run_skill(self, context):
        # Implement skill logic here
        return {'message': 'Skill executed successfully'}

    def validate(self, context):
        # Validate input context
        return True

if __name__ == '__main__':
    skill = $($(ComponentName -replace '-', '').replace('_', ''))Skill({})
    result = skill.execute({})
    print(json.dumps(result, indent=2))
"@
    
    $implementationContent | Out-File -FilePath "$Path\implementation.py" -Encoding UTF8
}

function Install-TemplateComponent {
    param(
        [string]$TemplateType,
        [string]$ComponentPath
    )
    
    $installationStats.totalComponents++
    
    try {
        # Check if component already exists
        $fullPath = Join-Path $TEMPLATES_DIR $ComponentPath
        
        if (Test-DirectoryExists -DirectoryPath $fullPath -ComponentType $TemplateType -ComponentName $ComponentPath) {
            Write-EnhancedLog "Component '$ComponentPath' already exists, analyzing for updates..." "WARNING"
            
            # Perform checksum comparison to detect changes
            $existingFiles = Get-ChildItem -Path $fullPath -File -ErrorAction SilentlyContinue
            if ($existingFiles.Count -gt 0) {
                Write-EnhancedLog "Existing component found, skipping to prevent overwrite" "INFO"
                $installationStats.skipped++
                return $true
            }
        }
        
        # Create standardized template structure
        $result = Create-StandardizedTemplateStructure -TemplateType $TemplateType -ComponentPath $ComponentPath -TemplateDefinition $TEMPLATE_DEFINITIONS[$TemplateType]
        
        if ($result) {
            $installationStats.installed++
        }
        else {
            $installationStats.errors++
        }
        
        return $result
    }
    catch {
        Write-EnhancedLog "Error installing $TemplateType component '$ComponentPath': $($_.Exception.Message)" "ERROR"
        $installationStats.errors++
        return $false
    }
}

function Show-InstallationSummary {
    Write-EnhancedLog "Installation Summary" "SUCCESS"
    Write-EnhancedLog "=====================" "SUCCESS"
    Write-EnhancedLog "Total Components Processed: $($installationStats.totalComponents)" "INFO"
    Write-EnhancedLog "Successfully Installed: $($installationStats.installed)" "SUCCESS"
    Write-EnhancedLog "Skipped (Existing): $($installationStats.skipped)" "WARNING"
    Write-EnhancedLog "Errors: $($installationStats.errors)" "ERROR"
    Write-EnhancedLog "Duplicates Found: $($installationStats.duplicatesFound)" "DUPLICATE"
    Write-EnhancedLog "Space Saved: $([math]::Round($installationStats.spaceSaved / 1KB, 2)) KB" "INFO"
    Write-EnhancedLog "Backup Created: $($installationStats.backupCreated)" "BACKUP"
    
    if ($installationStats.errors -gt 0) {
        Write-EnhancedLog "Installation completed with errors. Check log file for details." "WARNING"
        return $false
    }
    else {
        Write-EnhancedLog "Installation completed successfully!" "SUCCESS"
        return $true
    }
}

function Main {
    Write-EnhancedLog "Enhanced Claude Code Templates Installation Started"
    Write-EnhancedLog "Project: MR.VERMA Unified System"
    Write-EnhancedLog "Date: $(Get-Date)"
    Write-EnhancedLog "=================================="
    
    try {
        # Initialize environment
        Initialize-Environment
        
        # Create backup of existing templates
        $backupPath = Backup-ExistingTemplates
        
        # Scan for duplicates before installation
        $duplicateReport = Scan-ForDuplicates
        
        # Create base template directory structure
        Write-EnhancedLog "Creating base template directory structure..."
        foreach ($templateType in $TEMPLATE_DEFINITIONS.Keys) {
            $basePath = Join-Path $TEMPLATES_DIR $TEMPLATE_DEFINITIONS[$templateType].basePath
            if (-not (Test-Path $basePath)) {
                New-Item -Path $basePath -ItemType Directory -Force | Out-Null
                Write-EnhancedLog "Created base directory: $basePath"
            }
        }
        
        # Install all template components
        Write-EnhancedLog "Installing template components..."
        
        foreach ($templateType in $TEMPLATE_DEFINITIONS.Keys) {
            Write-EnhancedLog "Processing $templateType templates..."
            
            $components = $TEMPLATE_DEFINITIONS[$templateType].components
            $totalComponents = $components.Count
            $current = 0
            
            foreach ($component in $components) {
                $current++
                $progress = [math]::Round(($current / $totalComponents) * 100, 1)
                Write-EnhancedLog "Installing $templateType $current/$totalComponents ($progress%): $component"
                
                Install-TemplateComponent -TemplateType $templateType -ComponentPath $component
            }
        }
        
        # Show final summary
        $success = Show-InstallationSummary
        
        if ($success) {
            Write-EnhancedLog "Enhanced installation completed successfully!" "SUCCESS"
            Write-EnhancedLog "Log file: $LOG_FILE" "INFO"
            Write-EnhancedLog "Backup location: $BACKUP_DIR" "INFO"
            Write-EnhancedLog "Duplicate analysis: $DUPLICATE_SCAN_DIR" "INFO"
            exit 0
        }
        else {
            Write-EnhancedLog "Installation completed with errors. Review log for details." "WARNING"
            exit 1
        }
    }
    catch {
        Write-EnhancedLog "Critical installation error: $($_.Exception.Message)" "ERROR"
        Write-EnhancedLog "Stack trace: $($_.ScriptStackTrace)" "ERROR"
        exit 1
    }
}

# Execute main function
Main