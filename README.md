# MR.VERMA v2.0.0
## Synchronized Intelligence Grid 🕸️

MR.VERMA is an advanced AI orchestration platform with SpiderWeb synchronization, supporting OPENCODE, TRAE.AI, and local execution environments.

---

## 🚀 Quick Start

### Windows
```batch
start.bat              # Auto-detect platform and start
start.bat opencode     # Force OPENCODE mode
start.bat traeai       # Force TRAE.AI mode
start.bat local        # Force Local mode
start.bat docker       # Start with Docker
```

### Linux/Mac
```bash
./start.sh             # Auto-detect platform and start
./start.sh opencode    # Force OPENCODE mode
./start.sh traeai      # Force TRAE.AI mode
./start.sh local       # Force Local mode
./start.sh docker      # Start with Docker
```

### NPM Scripts
```bash
npm start              # Start MR.VERMA
npm run start:opencode # Start in OPENCODE mode
npm run start:traeai   # Start in TRAE.AI mode
npm run start:local    # Start in Local mode
npm run agents         # Show all agents
npm run skills         # Show all skills
npm run workflows      # Show all workflows
npm run status         # Show system status
npm run sync           # Sync SpiderWeb
```

---

## 📁 Project Structure

```
MR.VERMA/
├── core/                           # Core system modules
│   ├── startup.js                  # Unified startup script
│   ├── orchestrator.js             # Main orchestrator
│   ├── agent-registry.js           # Agent management
│   ├── skills-loader.js            # Skills loader
│   ├── workflow-engine.js          # Workflow execution
│   ├── platform-adapter.js         # Platform integration
│   └── traeai-integration.js       # TRAE.AI specific module
├── config/
│   └── verma.yaml                  # Main configuration
├── opencodespec.yaml               # OPENCODE specification
├── plantskills/workflows/          # 126+ workflow skills
├── index.js                        # Main entry point
├── start.bat                       # Windows startup
├── start.sh                        # Unix startup
├── package.json                    # NPM configuration
└── .env.example                    # Environment template
```

---

## 🤖 Agents (12+ Specialized)

| Agent | Role | Description |
|-------|------|-------------|
| **Orchestrator** | Central Brain | SpiderWeb coordination hub |
| **Frontend Specialist** | Developer | React, Vue, Angular expert |
| **Backend Specialist** | Developer | Node.js, Python, API design |
| **Security Auditor** | Auditor | Security analysis & scanning |
| **Senior Architect** | Planner | System design & architecture |
| **Test Engineer** | QA | Testing & quality assurance |
| **DevOps Engineer** | Operations | CI/CD & infrastructure |
| **Product Manager** | Management | Requirements & roadmap |
| **Performance Optimizer** | Optimizer | Performance tuning |
| **Documentation Writer** | Writer | Technical documentation |
| **AI Specialist** | AI Expert | ML & AI integration |
| **Mobile Developer** | Mobile Dev | iOS & Android development |

---

## 🛠️ Skills (126+ Workflows)

All skills are stored in `plantskills/workflows/` and include:

- **Security**: vulnerability-scanner, secure-audit, security-review
- **Testing**: testing-patterns, tdd-workflow, qa-automation
- **Frontend**: web-design-guidelines, ui-ux-pro-max, responsive-design
- **Backend**: nodejs-best-practices, api-design, database-patterns
- **DevOps**: docker-deployment, ci-cd-pipeline, kubernetes
- **Performance**: memory-optimization, token-efficiency, profiling
- **Mobile**: ios-design, android-design, react-native
- **Architecture**: software-architecture, system-design, c4-diagrams
- **AI/ML**: langchain-architecture, model-integration, nlp-patterns

---

## ⚡ Workflows

### Core Workflows
- **startup**: Initialize system, load agents & skills
- **code_review**: Comprehensive code review process
- **feature_development**: End-to-end feature development
- **security_audit**: Security vulnerability scanning
- **optimization**: Performance optimization
- **documentation**: Generate comprehensive docs

### Workflow Features
- Sequential execution
- Parallel execution
- Agent task routing
- Validation steps
- Sub-workflows
- Error handling

---

## 🔌 Platform Integration

### OPENCODE
```yaml
# opencodespec.yaml
agents:
  - orchestrator
  - frontend_specialist
  - backend_specialist
  - security_auditor
  
commands:
  verma: Main orchestration
  analyze: Code analysis
  plan: Project planning
  build: Feature building
  test: Run tests
```

### TRAE.AI
- Automatic platform detection
- Native command integration
- Real-time file monitoring
- Project-aware context
- Notification system

### Local
- Docker Compose support
- Agent Lightning integration
- Local LLM support
- Full offline capability

---

## 🕸️ SpiderWeb Architecture

```
User Request
     ↓
Orchestrator (SpiderWeb Hub)
     ↓
┌─────┴─────┬─────────┬──────────┐
↓           ↓         ↓          ↓
Agent 1   Agent 2   Agent 3   Agent N
  ↓           ↓         ↓          ↓
  └───────────┴─────────┴──────────┘
              ↓
         Synchronized
         Execution
```

---

## 📊 Power Usage Features

### Symbolic Density
- Compressed notation (∴, ∵, →)
- 70% smaller footprint
- Identical quality output
- Reduced token costs

### Memory Optimization
- Skill caching
- Agent state management
- Workflow persistence
- Efficient routing

---

## ⚙️ Configuration

### Environment Variables
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env
VERMA_PLATFORM=auto
OPENCODE_ENABLED=true
TRAE_AI_ENABLED=true
AGENTS_AUTO_START=true
SKILLS_AUTO_LOAD=true
```

### Platform Detection
MR.VERMA automatically detects the platform based on:
1. Environment variables (`OPENCODE_ENV`, `TRAE_AI_ENV`)
2. Marker files (`.opencode`, `.trae`)
3. Default to local mode

---

## 🔧 Development

### Prerequisites
- Node.js 16+
- NPM or Yarn
- (Optional) Docker

### Installation
```bash
git clone <repository>
cd MR.VERMA
npm install
npm start
```

### Adding New Agents
```javascript
// core/agent-registry.js
registerAgent({
  id: 'new_agent',
  name: 'New Agent',
  role: 'specialist',
  capabilities: ['capability1', 'capability2'],
  auto_start: true
});
```

### Adding New Skills
1. Create Markdown file in `plantskills/workflows/`
2. Follow existing skill format
3. Run `npm run skills` to verify

### Adding New Workflows
```javascript
// core/workflow-engine.js
registerWorkflow('custom_workflow', {
  name: 'Custom Workflow',
  description: 'Description',
  steps: [...],
  auto_execute: false
});
```

---

## 📈 System Status

Run `npm run status` to see:
- Platform (OPENCODE/TRAE.AI/Local)
- Active agents
- Loaded skills
- Running workflows
- System uptime

---

## 🤝 Integration Examples

### OPENCODE
```javascript
// Auto-registered on startup
verma.analyze('./src')
verma.plan('Build new feature')
verma.build('Create login form')
```

### TRAE.AI
```javascript
// Available as commands
/verma.analyze
/verma.secure
/verma.optimize
```

### Local API
```javascript
const Verma = require('./core/startup');
const verma = new Verma();
await verma.start();
await verma.orchestrator.handleCommand('analyze', { target: './src' });
```

---

## 🛡️ Security

- Security audit workflows
- Vulnerability scanning
- Automated security checks
- Code review integration

---

## 📄 License

MIT License - See LICENSE file

---

## 🔗 Links

- Documentation: See `PRODUCT DOCUMT/USER_GUIDE.md`
- Skills: `plantskills/workflows/`
- Configuration: `config/verma.yaml`

---

## 🙏 Credits

MR.VERMA - Synchronized Intelligence Grid
Built for OPENCODE, TRAE.AI, and beyond.
