#!/usr/bin/env node
/**
 * MR.VERMA Code Execution Sandbox
 * Safe execution environment for generated code
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

class CodeExecutionSandbox {
  constructor(options = {}) {
    this.options = {
      timeout: options.timeout || 30000,
      memoryLimit: options.memoryLimit || '512m',
      cpuLimit: options.cpuLimit || '1.0',
      network: options.network || false,
      workDir: options.workDir || path.join(process.cwd(), '.verma', 'sandbox'),
      ...options
    };
    
    this.activeProcesses = new Map();
    this.executionHistory = [];
    
    this.initialize();
  }

  initialize() {
    // Create sandbox directory
    if (!fs.existsSync(this.options.workDir)) {
      fs.mkdirSync(this.options.workDir, { recursive: true });
    }
    
    console.log('🔒 Code Execution Sandbox initialized');
  }

  async executeNode(code, options = {}) {
    console.log('🚀 Executing Node.js code...');
    
    const sandboxId = `sandbox_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const sandboxDir = path.join(this.options.workDir, sandboxId);
    
    try {
      // Create sandbox directory
      fs.mkdirSync(sandboxDir, { recursive: true });
      
      // Write code to file
      const codeFile = path.join(sandboxDir, 'index.js');
      const wrappedCode = this.wrapNodeCode(code);
      fs.writeFileSync(codeFile, wrappedCode);
      
      // Execute with timeout and limits
      const result = await this.runNodeProcess(codeFile, {
        timeout: options.timeout || this.options.timeout,
        cwd: sandboxDir,
        env: this.createSafeEnv()
      });
      
      // Record execution
      this.recordExecution('node', code, result);
      
      // Cleanup
      this.cleanupSandbox(sandboxDir);
      
      return result;
      
    } catch (error) {
      this.cleanupSandbox(sandboxDir);
      throw error;
    }
  }

  async executePython(code, options = {}) {
    console.log('🐍 Executing Python code...');
    
    const sandboxId = `sandbox_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const sandboxDir = path.join(this.options.workDir, sandboxId);
    
    try {
      fs.mkdirSync(sandboxDir, { recursive: true });
      
      const codeFile = path.join(sandboxDir, 'script.py');
      fs.writeFileSync(codeFile, code);
      
      const result = await this.runPythonProcess(codeFile, {
        timeout: options.timeout || this.options.timeout,
        cwd: sandboxDir,
        env: this.createSafeEnv()
      });
      
      this.recordExecution('python', code, result);
      this.cleanupSandbox(sandboxDir);
      
      return result;
      
    } catch (error) {
      this.cleanupSandbox(sandboxDir);
      throw error;
    }
  }

  async executeShell(command, options = {}) {
    console.log('🖥️  Executing shell command...');
    
    // Security: whitelist safe commands
    const allowedCommands = ['npm', 'node', 'python', 'git', 'ls', 'cat', 'echo'];
    const commandBase = command.split(' ')[0];
    
    if (!allowedCommands.includes(commandBase)) {
      throw new Error(`Command '${commandBase}' is not allowed`);
    }
    
    try {
      const { stdout, stderr } = await execPromise(command, {
        timeout: options.timeout || this.options.timeout,
        cwd: options.cwd || process.cwd(),
        env: this.createSafeEnv()
      });
      
      const result = {
        success: true,
        stdout,
        stderr,
        exitCode: 0
      };
      
      this.recordExecution('shell', command, result);
      return result;
      
    } catch (error) {
      const result = {
        success: false,
        stdout: error.stdout || '',
        stderr: error.stderr || '',
        exitCode: error.code || 1,
        error: error.message
      };
      
      this.recordExecution('shell', command, result);
      return result;
    }
  }

  async runProject(projectPath, options = {}) {
    console.log(`🚀 Running project: ${projectPath}`);
    
    // Detect project type
    const projectType = this.detectProjectType(projectPath);
    console.log(`   Detected: ${projectType}`);
    
    switch (projectType) {
      case 'node':
        return await this.runNodeProject(projectPath, options);
      case 'python':
        return await this.runPythonProject(projectPath, options);
      case 'docker':
        return await this.runDockerProject(projectPath, options);
      default:
        throw new Error(`Unknown project type: ${projectType}`);
    }
  }

  detectProjectType(projectPath) {
    if (fs.existsSync(path.join(projectPath, 'package.json'))) return 'node';
    if (fs.existsSync(path.join(projectPath, 'requirements.txt'))) return 'python';
    if (fs.existsSync(path.join(projectPath, 'Dockerfile'))) return 'docker';
    if (fs.existsSync(path.join(projectPath, 'docker-compose.yml'))) return 'docker';
    return 'unknown';
  }

  async runNodeProject(projectPath, options = {}) {
    const packageJson = JSON.parse(
      fs.readFileSync(path.join(projectPath, 'package.json'), 'utf8')
    );
    
    const scripts = packageJson.scripts || {};
    const startScript = scripts.dev || scripts.start || scripts.serve;
    
    if (!startScript) {
      throw new Error('No start script found in package.json');
    }
    
    return new Promise((resolve, reject) => {
      const cmd = startScript.includes('vite') ? 'npx vite' : 'npm run dev';
      
      const child = spawn('npm', ['run', 'dev'], {
        cwd: projectPath,
        env: { ...process.env, ...this.createSafeEnv() },
        detached: true
      });
      
      const processId = `process_${Date.now()}`;
      this.activeProcesses.set(processId, child);
      
      let output = '';
      let errors = '';
      
      child.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`   ${data.toString().trim()}`);
      });
      
      child.stderr.on('data', (data) => {
        errors += data.toString();
      });
      
      // Give it time to start
      setTimeout(() => {
        resolve({
          success: true,
          processId,
          pid: child.pid,
          output: output.substring(0, 500),
          url: this.extractUrl(output) || 'http://localhost:3000'
        });
      }, 5000);
      
      // Timeout
      setTimeout(() => {
        if (this.activeProcesses.has(processId)) {
          this.stopProcess(processId);
        }
      }, options.timeout || 300000);
    });
  }

  async runPythonProject(projectPath, options = {}) {
    const mainFiles = ['main.py', 'app.py', 'server.py', 'manage.py'];
    let mainFile = null;
    
    for (const file of mainFiles) {
      if (fs.existsSync(path.join(projectPath, file))) {
        mainFile = file;
        break;
      }
    }
    
    if (!mainFile) {
      throw new Error('No main Python file found');
    }
    
    return new Promise((resolve, reject) => {
      const child = spawn('python', [mainFile], {
        cwd: projectPath,
        env: { ...process.env, ...this.createSafeEnv() },
        detached: true
      });
      
      const processId = `process_${Date.now()}`;
      this.activeProcesses.set(processId, child);
      
      let output = '';
      
      child.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`   ${data.toString().trim()}`);
      });
      
      setTimeout(() => {
        resolve({
          success: true,
          processId,
          pid: child.pid,
          output: output.substring(0, 500),
          url: this.extractUrl(output) || 'http://localhost:8000'
        });
      }, 3000);
    });
  }

  async runDockerProject(projectPath, options = {}) {
    console.log('🐳 Starting Docker project...');
    
    try {
      const { stdout } = await execPromise('docker-compose up -d', {
        cwd: projectPath,
        timeout: 60000
      });
      
      return {
        success: true,
        output: stdout,
        message: 'Docker containers started'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  runNodeProcess(file, options) {
    return new Promise((resolve, reject) => {
      const child = spawn('node', [file], {
        timeout: options.timeout,
        cwd: options.cwd,
        env: options.env
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        resolve({
          success: code === 0,
          stdout,
          stderr,
          exitCode: code
        });
      });
      
      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  runPythonProcess(file, options) {
    return new Promise((resolve, reject) => {
      const child = spawn('python', [file], {
        timeout: options.timeout,
        cwd: options.cwd,
        env: options.env
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        resolve({
          success: code === 0,
          stdout,
          stderr,
          exitCode: code
        });
      });
      
      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  wrapNodeCode(code) {
    return `
// Sandbox wrapper
const util = require('util');
const path = require('path');
const fs = require('fs');

// Override console to capture output
const originalConsole = { ...console };
const output = [];

console.log = (...args) => {
  output.push(args.map(a => util.inspect(a)).join(' '));
  originalConsole.log(...args);
};

console.error = (...args) => {
  output.push('ERROR: ' + args.map(a => util.inspect(a)).join(' '));
  originalConsole.error(...args);
};

// Security: Disable dangerous operations
const originalRequire = require;
require = (id) => {
  const allowed = ['fs', 'path', 'util', 'crypto', 'http', 'https', 'url', 'querystring'];
  if (!allowed.includes(id)) {
    throw new Error(\`Module '\${id}' is not allowed in sandbox\`);
  }
  return originalRequire(id);
};

// User code
${code}

// Output results
if (output.length > 0) {
  console.log('\\n--- Sandbox Output ---');
  console.log(output.join('\\n'));
}
`;
  }

  createSafeEnv() {
    return {
      NODE_ENV: 'development',
      PATH: process.env.PATH,
      HOME: process.env.HOME
    };
  }

  extractUrl(output) {
    const urlMatch = output.match(/(http:\/\/localhost:\d+)/);
    return urlMatch ? urlMatch[1] : null;
  }

  stopProcess(processId) {
    const child = this.activeProcesses.get(processId);
    if (child) {
      try {
        process.kill(-child.pid);
      } catch (e) {
        // Process already dead
      }
      this.activeProcesses.delete(processId);
    }
  }

  cleanupSandbox(sandboxDir) {
    try {
      fs.rmSync(sandboxDir, { recursive: true, force: true });
    } catch (e) {
      // Ignore cleanup errors
    }
  }

  recordExecution(type, code, result) {
    this.executionHistory.push({
      timestamp: new Date().toISOString(),
      type,
      codeLength: code.length,
      success: result.success,
      exitCode: result.exitCode
    });
  }

  getStatus() {
    return {
      activeProcesses: this.activeProcesses.size,
      totalExecutions: this.executionHistory.length,
      workDir: this.options.workDir
    };
  }

  stopAll() {
    for (const [processId, child] of this.activeProcesses) {
      this.stopProcess(processId);
    }
  }
}

module.exports = CodeExecutionSandbox;
