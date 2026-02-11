#!/usr/bin/env node
/**
 * MR.VERMA Vibecoding Agent
 * Natural language to application development
 * Version: 2.0.0
 */

const fs = require('fs');
const path = require('path');
const LocalLLMManager = require('./local-llm');

class VibecodingAgent {
  constructor(orchestrator) {
    this.orchestrator = orchestrator;
    this.llm = null;
    this.activeProjects = new Map();
    this.templates = this.loadTemplates();
  }

  async initialize() {
    console.log('🎨 Initializing Vibecoding Agent...');
    
    // Initialize local LLM connection
    this.llm = new LocalLLMManager({
      provider: 'ollama',
      model: 'codellama:7b-code',
      temperature: 0.7,
      maxTokens: 4096
    });
    
    await this.llm.initialize();
    
    console.log('✅ Vibecoding Agent ready');
    return this;
  }

  loadTemplates() {
    return {
      'react-app': {
        type: 'react-app',
        name: 'React Application',
        stack: ['React', 'Vite', 'Tailwind CSS'],
        files: ['package.json', 'vite.config.js', 'src/App.jsx', 'src/main.jsx', 'index.html', 'tailwind.config.js'],
        description: 'Modern React application with Vite and Tailwind'
      },
      'nextjs-app': {
        type: 'nextjs-app',
        name: 'Next.js Application',
        stack: ['Next.js', 'React', 'Tailwind CSS'],
        files: ['package.json', 'next.config.js', 'pages/index.js', 'styles/globals.css', 'tailwind.config.js'],
        description: 'Full-stack Next.js application'
      },
      'vue-app': {
        type: 'vue-app',
        name: 'Vue Application',
        stack: ['Vue 3', 'Vite', 'Tailwind CSS'],
        files: ['package.json', 'vite.config.js', 'src/App.vue', 'src/main.js', 'index.html'],
        description: 'Modern Vue 3 application'
      },
      'python-api': {
        type: 'python-api',
        name: 'Python API',
        stack: ['Python', 'FastAPI', 'Uvicorn'],
        files: ['requirements.txt', 'main.py', 'app/__init__.py', 'app/routers.py', 'app/models.py'],
        description: 'FastAPI-based REST API'
      },
      'node-api': {
        type: 'node-api',
        name: 'Node.js API',
        stack: ['Node.js', 'Express', 'TypeScript'],
        files: ['package.json', 'tsconfig.json', 'src/index.ts', 'src/app.ts', 'src/routes.ts'],
        description: 'Express-based REST API with TypeScript'
      },
      'mobile-app': {
        type: 'mobile-app',
        name: 'React Native App',
        stack: ['React Native', 'Expo', 'TypeScript'],
        files: ['package.json', 'App.tsx', 'app.json', 'tsconfig.json'],
        description: 'Cross-platform mobile application'
      }
    };
  }

  async processRequest(description, options = {}) {
    console.log('🎨 Processing vibecoding request...');
    console.log(`   Description: ${description.substring(0, 100)}...`);
    
    // Step 1: Analyze requirements
    const analysis = await this.analyzeRequirements(description);
    console.log(`   Detected type: ${analysis.type}`);
    console.log(`   Confidence: ${analysis.confidence}%`);
    
    // Step 2: Select template
    const template = this.selectTemplate(analysis);
    console.log(`   Template: ${template.name}`);
    
    // Step 3: Generate project plan
    const plan = await this.generateProjectPlan(description, analysis, template);
    
    // Step 4: Create project structure
    const project = await this.createProject(plan, options);
    
    // Step 5: Generate code with local LLM
    const generatedCode = await this.generateCode(plan, template);
    
    // Step 6: Write files
    await this.writeProjectFiles(project, generatedCode);
    
    // Step 7: Validate and optimize
    const validation = await this.validateProject(project);
    
    return {
      project,
      plan,
      analysis,
      generatedCode,
      validation,
      summary: {
        filesCreated: Object.keys(generatedCode).length,
        template: template.name,
        stack: template.stack,
        location: project.path
      }
    };
  }

  async analyzeRequirements(description) {
    const lower = description.toLowerCase();
    
    // Detect app type
    let type = 'react-app';
    let confidence = 50;
    
    if (/mobile|ios|android|app/i.test(lower)) {
      type = 'mobile-app';
      confidence = 90;
    } else if (/next\.?js|full.?stack/i.test(lower)) {
      type = 'nextjs-app';
      confidence = 90;
    } else if (/vue/i.test(lower)) {
      type = 'vue-app';
      confidence = 90;
    } else if (/python|fastapi|flask/i.test(lower)) {
      type = 'python-api';
      confidence = 90;
    } else if (/node|express|api/i.test(lower)) {
      type = 'node-api';
      confidence = 85;
    } else if (/react/i.test(lower)) {
      type = 'react-app';
      confidence = 95;
    }
    
    // Extract features
    const features = [];
    if (/auth|login|user/i.test(lower)) features.push('authentication');
    if (/database|db|storage/i.test(lower)) features.push('database');
    if (/api|rest|endpoint/i.test(lower)) features.push('api');
    if (/dashboard|admin/i.test(lower)) features.push('dashboard');
    if (/chat|messaging/i.test(lower)) features.push('chat');
    if (/payment|stripe/i.test(lower)) features.push('payments');
    if (/search/i.test(lower)) features.push('search');
    if (/upload|file/i.test(lower)) features.push('file-upload');
    
    return {
      type,
      confidence,
      features,
      description: description.substring(0, 500),
      complexity: this.assessComplexity(description, features)
    };
  }

  assessComplexity(description, features) {
    let score = 0;
    
    // Base complexity from features
    score += features.length * 10;
    
    // Length complexity
    if (description.length > 500) score += 20;
    if (description.length > 1000) score += 30;
    
    // Keywords
    if (/complex|advanced|enterprise/i.test(description)) score += 30;
    if (/simple|basic|minimal/i.test(description)) score -= 20;
    
    if (score < 30) return { level: 'simple', score, hours: 2 };
    if (score < 60) return { level: 'moderate', score, hours: 4 };
    if (score < 100) return { level: 'complex', score, hours: 8 };
    return { level: 'enterprise', score, hours: 16 };
  }

  selectTemplate(analysis) {
    return this.templates[analysis.type] || this.templates['react-app'];
  }

  async generateProjectPlan(description, analysis, template) {
    const projectName = this.extractProjectName(description) || 'my-app';
    
    return {
      name: projectName,
      type: analysis.type,
      template: template.name,
      stack: template.stack,
      features: analysis.features,
      complexity: analysis.complexity,
      description: description,
      files: template.files,
      architecture: {
        frontend: template.stack.filter(s => /react|vue|angular|next/i.test(s)),
        backend: template.stack.filter(s => /node|python|express|fastapi/i.test(s)),
        database: analysis.features.includes('database') ? 'SQLite/PostgreSQL' : null,
        hosting: 'Local development'
      },
      pages: this.inferPages(description),
      components: this.inferComponents(description)
    };
  }

  extractProjectName(description) {
    // Try to extract project name from description
    const matches = description.match(/(?:called|named)\s+["']?([\w-]+)["']?/i);
    if (matches) return matches[1];
    
    // Extract from "Build a X" pattern
    const buildMatch = description.match(/(?:build|create)\s+(?:a|an)\s+(\w+)/i);
    if (buildMatch) return `${buildMatch[1]}-app`;
    
    return null;
  }

  inferPages(description) {
    const pages = ['Home'];
    const lower = description.toLowerCase();
    
    if (/about/i.test(lower)) pages.push('About');
    if (/contact/i.test(lower)) pages.push('Contact');
    if (/login|signin/i.test(lower)) pages.push('Login');
    if (/register|signup/i.test(lower)) pages.push('Register');
    if (/dashboard/i.test(lower)) pages.push('Dashboard');
    if (/profile/i.test(lower)) pages.push('Profile');
    if (/settings/i.test(lower)) pages.push('Settings');
    if (/admin/i.test(lower)) pages.push('Admin');
    
    return pages;
  }

  inferComponents(description) {
    const components = ['Header', 'Footer', 'Layout'];
    const lower = description.toLowerCase();
    
    if (/button/i.test(lower)) components.push('Button');
    if (/form|input/i.test(lower)) components.push('Form', 'Input');
    if (/card/i.test(lower)) components.push('Card');
    if (/modal|popup/i.test(lower)) components.push('Modal');
    if (/nav|menu/i.test(lower)) components.push('Navigation', 'Sidebar');
    if (/table|list/i.test(lower)) components.push('DataTable', 'List');
    if (/chart|graph/i.test(lower)) components.push('Chart');
    if (/map/i.test(lower)) components.push('Map');
    
    return [...new Set(components)];
  }

  async createProject(plan, options) {
    const projectId = `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const outputDir = options.outputDir || path.join(process.cwd(), 'projects');
    const projectPath = path.join(outputDir, plan.name);
    
    // Create directory structure
    if (!fs.existsSync(projectPath)) {
      fs.mkdirSync(projectPath, { recursive: true });
    }
    
    const project = {
      id: projectId,
      name: plan.name,
      path: projectPath,
      plan: plan,
      createdAt: new Date().toISOString(),
      status: 'initializing'
    };
    
    this.activeProjects.set(projectId, project);
    
    return project;
  }

  async generateCode(plan, template) {
    const generated = {};
    
    // If LLM is connected, use it for intelligent generation
    if (this.llm && this.llm.status === 'connected') {
      console.log('🤖 Using Local LLM for intelligent code generation...');
      
      for (const file of plan.files) {
        const prompt = this.createCodeGenerationPrompt(plan, file, template);
        try {
          const result = await this.llm.generate(prompt, {
            temperature: 0.7,
            maxTokens: 4096
          });
          // Ensure we have valid content
          generated[file] = result.text || this.getTemplateCode(file, template);
        } catch (error) {
          console.warn(`   Failed to generate ${file}, using template: ${error.message}`);
          generated[file] = this.getTemplateCode(file, template);
        }
      }
    } else {
      // Use template code
      console.log('📝 Using template-based code generation...');
      for (const file of plan.files) {
        const code = this.getTemplateCode(file, template);
        generated[file] = code || `// ${file}\n// Generated by MR.VERMA`;
      }
    }
    
    return generated;
  }

  createCodeGenerationPrompt(plan, file, template) {
    return `You are an expert developer creating a ${template.name}.

Project: ${plan.name}
Description: ${plan.description}
Features: ${plan.features.join(', ')}
Pages: ${plan.pages.join(', ')}
Components: ${plan.components.join(', ')}

Generate the complete code for file: ${file}

Requirements:
- Use ${template.stack.join(', ')}
- Include all necessary imports
- Make it production-ready
- Include comments explaining key parts
- Follow best practices

Output ONLY the code, no explanations.`;
  }

  getTemplateCode(file, template) {
    const templates = {
      'package.json': this.getPackageJsonTemplate(template),
      'src/App.jsx': this.getReactAppTemplate(template),
      'src/main.jsx': this.getReactMainTemplate(template),
      'vite.config.js': this.getViteConfigTemplate(template),
      'index.html': this.getIndexHtmlTemplate(template),
      'tailwind.config.js': this.getTailwindConfigTemplate(template)
    };
    
    return templates[file] || `// ${file}\n// Generated by MR.VERMA Vibecoding Agent`;
  }

  getPackageJsonTemplate(template) {
    const isReact = template.type === 'react-app';
    const isNext = template.type === 'nextjs-app';
    
    if (isReact) {
      return JSON.stringify({
        name: template.name.toLowerCase().replace(/\s+/g, '-'),
        version: '1.0.0',
        type: 'module',
        scripts: {
          dev: 'vite',
          build: 'vite build',
          preview: 'vite preview'
        },
        dependencies: {
          react: '^18.2.0',
          'react-dom': '^18.2.0'
        },
        devDependencies: {
          '@types/react': '^18.2.43',
          '@types/react-dom': '^18.2.17',
          '@vitejs/plugin-react': '^4.2.1',
          autoprefixer: '^10.4.16',
          postcss: '^8.4.32',
          tailwindcss: '^3.4.0',
          vite: '^5.0.8'
        }
      }, null, 2);
    }
    
    return JSON.stringify({
      name: template.name.toLowerCase().replace(/\s+/g, '-'),
      version: '1.0.0',
      scripts: { start: 'echo "Start script here"' }
    }, null, 2);
  }

  getReactAppTemplate(template) {
    return `import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            ${template.name}
          </h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            Welcome to your new app!
          </h2>
          <p className="text-gray-600">
            Built with ${template.stack.join(', ')}
          </p>
          <div className="mt-4">
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Get Started
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;`;
  }

  getReactMainTemplate(template) {
    return `import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);`;
  }

  getViteConfigTemplate(template) {
    return `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
});`;
  }

  getIndexHtmlTemplate(template) {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${template.name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>`;
  }

  getTailwindConfigTemplate(template) {
    return `/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}`;
  }

  async writeProjectFiles(project, generatedCode) {
    console.log('📝 Writing project files...');
    
    for (const [filePath, content] of Object.entries(generatedCode)) {
      // Skip if content is undefined or null
      if (content === undefined || content === null) {
        console.warn(`   ⚠️  Skipping ${filePath} - no content generated`);
        continue;
      }
      
      const fullPath = path.join(project.path, filePath);
      const dir = path.dirname(fullPath);
      
      // Create directory if needed
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      // Write file
      fs.writeFileSync(fullPath, content);
      console.log(`   ✓ ${filePath}`);
    }
    
    // Create README
    const readme = this.generateReadme(project);
    fs.writeFileSync(path.join(project.path, 'README.md'), readme);
    
    // Create .gitignore
    const gitignore = `node_modules/
dist/
.env
.env.local
*.log`;
    fs.writeFileSync(path.join(project.path, '.gitignore'), gitignore);
    
    project.status = 'completed';
  }

  generateReadme(project) {
    return `# ${project.plan.name}

${project.plan.description}

## Tech Stack
${project.plan.stack.map(s => `- ${s}`).join('\n')}

## Features
${project.plan.features.map(f => `- ${f}`).join('\n')}

## Pages
${project.plan.pages.map(p => `- ${p}`).join('\n')}

## Components
${project.plan.components.map(c => `- ${c}`).join('\n')}

## Getting Started

\`\`\`bash
# Install dependencies
npm install

# Start development server
npm run dev
\`\`\`

## Built with MR.VERMA Vibecoding Agent 🤖
`;
  }

  async validateProject(project) {
    console.log('✅ Validating project...');
    
    const checks = {
      hasPackageJson: fs.existsSync(path.join(project.path, 'package.json')),
      hasEntryFile: fs.existsSync(path.join(project.path, 'src', 'App.jsx')) ||
                    fs.existsSync(path.join(project.path, 'src', 'App.tsx')),
      hasReadme: fs.existsSync(path.join(project.path, 'README.md')),
      fileCount: fs.readdirSync(project.path, { recursive: true }).length
    };
    
    return {
      valid: checks.hasPackageJson && checks.hasEntryFile,
      checks,
      recommendations: []
    };
  }

  getStatus() {
    return {
      llmStatus: this.llm?.getStatus() || { status: 'disconnected' },
      activeProjects: this.activeProjects.size,
      templates: Object.keys(this.templates)
    };
  }
}

module.exports = VibecodingAgent;
