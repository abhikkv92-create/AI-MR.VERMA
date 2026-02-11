#!/usr/bin/env node
/**
 * MR.VERMA Interactive CLI
 * Enhanced startup with chat interface and vibecoding
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const EnhancedVermaOrchestrator = require('./core/enhanced-orchestrator');

class VermaInteractiveCLI {
  constructor() {
    this.orchestrator = null;
    this.rl = null;
    this.running = false;
  }

  async start() {
    this.printBanner();
    
    // Initialize orchestrator
    this.orchestrator = new EnhancedVermaOrchestrator();
    await this.orchestrator.initialize();
    
    // Setup interactive mode
    this.setupInteractiveMode();
    
    console.log('\n🚀 Ready! Type your request or "help" for commands.\n');
    
    this.running = true;
    this.prompt();
  }

  printBanner() {
    console.clear();
    console.log('\n');
    console.log('╔══════════════════════════════════════════════════════════════╗');
    console.log('║                                                              ║');
    console.log('║           🕸️  MR.VERMA ENHANCED SPIDER WEB  🕸️            ║');
    console.log('║                                                              ║');
    console.log('║              Vibecoding + Local LLM + Chat                 ║');
    console.log('║                      Version 2.0.0                          ║');
    console.log('║                                                              ║');
    console.log('╚══════════════════════════════════════════════════════════════╝');
    console.log('\n');
  }

  setupInteractiveMode() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '🕸️  > '
    });

    this.rl.on('line', async (input) => {
      await this.handleInput(input.trim());
      if (this.running) this.prompt();
    });

    this.rl.on('close', () => {
      this.shutdown();
    });

    // Handle Ctrl+C
    process.on('SIGINT', () => {
      this.shutdown();
    });
  }

  prompt() {
    this.rl.prompt();
  }

  async handleInput(input) {
    if (!input) return;

    // Check for command prefix
    if (input.startsWith('/verma ') || input.startsWith('/v ')) {
      const command = input.replace(/^\/verma\s*/, '').replace(/^\/v\s*/, '');
      await this.handleCommand(command);
      return;
    }

    // Check for special commands
    if (input.startsWith('/')) {
      await this.handleSlashCommand(input);
      return;
    }

    // Check if it's a build request
    if (this.isBuildRequest(input)) {
      await this.handleBuildRequest(input);
      return;
    }

    // Treat as chat message
    await this.handleChat(input);
  }

  isBuildRequest(input) {
    const buildPatterns = [
      /^(build|create|make)\s+/i,
      /^(i want|i need)\s+(a|an)\s+/i,
      /^can you (build|create|make)/i,
      /^help me (build|create|make)/i
    ];
    
    return buildPatterns.some(pattern => pattern.test(input));
  }

  async handleCommand(command) {
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1).join(' ');

    try {
      switch (cmd) {
        case 'chat':
          console.log('\n💬 Starting chat mode. Type your messages (type "exit" to quit):\n');
          this.chatMode = true;
          break;
        case 'build':
        case 'create':
          if (args) {
            await this.orchestrator.startBuild({ description: args });
          } else {
            console.log('❌ Please provide a description: /verma build [description]');
          }
          break;
        case 'vibe':
        case 'vibecode':
          if (args) {
            await this.orchestrator.startVibecoding({ description: args });
          } else {
            console.log('❌ Please provide a description: /verma vibe [description]');
          }
          break;
        case 'status':
          await this.orchestrator.getFullStatus();
          break;
        case 'agents':
          this.orchestrator.showAgents();
          break;
        case 'skills':
          this.orchestrator.showSkills();
          break;
        case 'workflows':
          this.orchestrator.showWorkflows();
          break;
        case 'llm':
          this.orchestrator.showLLMStatus();
          break;
        case 'sync':
          await this.orchestrator.registry.syncSpiderWeb();
          console.log('✅ SpiderWeb synchronized');
          break;
        case 'help':
        case '?':
          this.showHelp();
          break;
        case 'exit':
        case 'quit':
          this.shutdown();
          break;
        default:
          console.log(`❌ Unknown command: ${cmd}. Type /verma help for available commands.`);
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
    }
  }

  async handleSlashCommand(input) {
    const command = input.slice(1).toLowerCase();
    
    switch (command) {
      case 'help':
      case '?':
        this.showHelp();
        break;
      case 'status':
        await this.orchestrator.getFullStatus();
        break;
      case 'exit':
      case 'quit':
        this.shutdown();
        break;
      default:
        console.log(`❌ Unknown command: /${command}`);
    }
  }

  async handleBuildRequest(input) {
    console.log('\n🎨 Detected build request. Starting vibecoding...\n');
    await this.orchestrator.startVibecoding({ description: input });
  }

  async handleChat(input) {
    if (input.toLowerCase() === 'exit') {
      this.chatMode = false;
      console.log('\n💬 Chat mode exited.\n');
      return;
    }

    try {
      const response = await this.orchestrator.chat.processMessage(input);
      console.log('\n🤖 Assistant:\n' + response.message + '\n');
      
      // Execute any actions
      if (response.actions && response.actions.length > 0) {
        for (const action of response.actions) {
          if (action.type === 'execute_workflow' && action.workflow === 'vibecoding') {
            console.log('\n⚡ Executing vibecoding workflow...\n');
            await this.orchestrator.startVibecoding(action.params);
          }
        }
      }
    } catch (error) {
      console.error('❌ Chat error:', error.message);
    }
  }

  showHelp() {
    console.log(`
🕸️  MR.VERMA Enhanced - Commands
${'='.repeat(60)}

QUICK COMMANDS:
  Just describe what you want:
  "Build a React dashboard with charts"
  "Create a Python API for user management"
  "Make a todo app with authentication"

CHAT MODE:
  /verma chat              Start interactive chat
  /chat                    Same as above

BUILDING:
  /verma build "desc"      Build application from description
  /verma vibe "desc"       Vibecode mode (natural language)
  /build "desc"            Short form

SYSTEM:
  /verma status            Show system status
  /verma agents            List active agents
  /verma skills            List loaded skills
  /verma workflows         List workflows
  /verma llm               Show LLM status
  /verma sync              Sync SpiderWeb
  /verma help              Show this help
  /exit or /quit           Exit MR.VERMA

EXAMPLES:
  /verma build "A landing page for a SaaS product"
  /verma vibe "Mobile app for tracking daily water intake"
  /verma create "API with user auth and CRUD operations"
`);
  }

  shutdown() {
    console.log('\n👋 Shutting down MR.VERMA...');
    this.running = false;
    
    if (this.rl) {
      this.rl.close();
    }
    
    // Stop any running processes in sandbox
    if (this.orchestrator?.sandbox) {
      this.orchestrator.sandbox.stopAll();
    }
    
    console.log('✅ Goodbye!');
    process.exit(0);
  }
}

// Main entry
if (require.main === module) {
  const cli = new VermaInteractiveCLI();
  cli.start().catch(console.error);
}

module.exports = VermaInteractiveCLI;
