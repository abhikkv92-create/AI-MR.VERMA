#!/usr/bin/env node
/**
 * MR.VERMA Skills Loader
 * Dynamically loads and validates all workflow skills
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class SkillsLoader {
  constructor(skillsDir = null) {
    this.skillsDir = skillsDir || path.join(__dirname, '..', 'plantskills', 'workflows');
    this.skills = new Map();
    this.categories = new Map();
  }

  async loadAllSkills() {
    console.log('🛠️  Loading MR.VERMA Skills...');
    
    if (!fs.existsSync(this.skillsDir)) {
      console.warn(`⚠️  Skills directory not found: ${this.skillsDir}`);
      return this.skills;
    }

    const files = fs.readdirSync(this.skillsDir)
      .filter(file => file.endsWith('.md'));

    console.log(`  Found ${files.length} skill files`);

    for (const file of files) {
      await this.loadSkill(file);
    }

    this.categorizeSkills();
    this.printSummary();

    return this.skills;
  }

  async loadSkill(filename) {
    const skillPath = path.join(this.skillsDir, filename);
    const content = fs.readFileSync(skillPath, 'utf8');
    
    const skillName = filename.replace('.md', '');
    const metadata = this.extractMetadata(content);
    
    const skill = {
      name: skillName,
      filename,
      content,
      metadata,
      path: skillPath,
      loadedAt: new Date().toISOString(),
      validated: this.validateSkill(content)
    };

    this.skills.set(skillName, skill);
    return skill;
  }

  extractMetadata(content) {
    const metadata = {
      title: null,
      description: null,
      category: 'general',
      tags: [],
      author: null,
      version: '1.0.0',
      compatible: []
    };

    // Extract title (first # heading)
    const titleMatch = content.match(/^# (.+)$/m);
    if (titleMatch) {
      metadata.title = titleMatch[1].trim();
    }

    // Extract description (first paragraph after title)
    const descMatch = content.match(/^# .+\n\n(.+?)(?:\n\n|$)/ms);
    if (descMatch) {
      metadata.description = descMatch[1].trim();
    }

    // Extract category from filename or content
    const categoryPatterns = {
      'security': /security|vulnerability|audit/i,
      'testing': /test|qa|validation/i,
      'frontend': /frontend|react|vue|angular|ui|ux/i,
      'backend': /backend|api|database|server/i,
      'devops': /deploy|ci\/cd|docker|kubernetes/i,
      'architecture': /architecture|design|pattern/i,
      'performance': /performance|optimization|memory|token/i,
      'mobile': /mobile|ios|android|app/i,
      'ai': /ai|ml|model|neural/i,
      'documentation': /doc|guide|reference/i
    };

    for (const [cat, pattern] of Object.entries(categoryPatterns)) {
      if (pattern.test(content)) {
        metadata.category = cat;
        break;
      }
    }

    // Extract tags
    const tagMatches = content.match(/\*\*Tags?\*\*:\s*(.+)/i);
    if (tagMatches) {
      metadata.tags = tagMatches[1].split(',').map(t => t.trim());
    }

    return metadata;
  }

  validateSkill(content) {
    const validations = {
      hasTitle: /^# .+$/m.test(content),
      hasDescription: content.length > 100,
      hasCode: /```[\s\S]+?```/.test(content),
      hasSections: /## .+/.test(content),
      hasPowerUsage: /poweruseage|optimization|token/i.test(content)
    };

    return {
      valid: Object.values(validations).every(v => v),
      score: Object.values(validations).filter(v => v).length / Object.keys(validations).length,
      checks: validations
    };
  }

  categorizeSkills() {
    for (const [name, skill] of this.skills) {
      const category = skill.metadata.category;
      if (!this.categories.has(category)) {
        this.categories.set(category, []);
      }
      this.categories.get(category).push(skill);
    }
  }

  printSummary() {
    console.log('\n📊 Skills Summary:');
    console.log(`  Total Skills: ${this.skills.size}`);
    
    for (const [category, skills] of this.categories) {
      console.log(`  ${category}: ${skills.length} skills`);
    }

    // Top rated skills
    const topSkills = Array.from(this.skills.values())
      .filter(s => s.validated.valid)
      .sort((a, b) => b.validated.score - a.validated.score)
      .slice(0, 5);

    if (topSkills.length > 0) {
      console.log('\n⭐ Top Validated Skills:');
      topSkills.forEach(s => {
        console.log(`  - ${s.name} (${Math.round(s.validated.score * 100)}% score)`);
      });
    }
  }

  getSkill(name) {
    return this.skills.get(name);
  }

  getSkillsByCategory(category) {
    return this.categories.get(category) || [];
  }

  searchSkills(query) {
    const results = [];
    const pattern = new RegExp(query, 'i');

    for (const [name, skill] of this.skills) {
      if (pattern.test(name) || 
          pattern.test(skill.content) ||
          skill.metadata.tags.some(t => pattern.test(t))) {
        results.push(skill);
      }
    }

    return results;
  }

  getSkillRecommendations(task) {
    // Simple keyword matching for recommendations
    const taskLower = task.toLowerCase();
    const recommendations = [];

    const mappings = {
      'security': ['security-review', 'vulnerability-scanner', 'secure-audit'],
      'test': ['testing-patterns', 'tdd-workflow', 'qa-automation'],
      'frontend': ['frontend-specialist', 'ui-ux-pro-max', 'web-design-guidelines'],
      'backend': ['nodejs-best-practices', 'backend-specialist', 'api-design'],
      'deploy': ['devops-pipeline', 'docker-compose', 'kubernetes'],
      'optimize': ['memory-optimization', 'token-efficiency', 'performance-profiling']
    };

    for (const [keyword, skills] of Object.entries(mappings)) {
      if (taskLower.includes(keyword)) {
        recommendations.push(...skills);
      }
    }

    return recommendations
      .map(name => this.getSkill(name))
      .filter(s => s !== undefined);
  }
}

// CLI usage
if (require.main === module) {
  const loader = new SkillsLoader();
  loader.loadAllSkills().then(() => {
    console.log('\n✅ Skills loading complete!');
  });
}

module.exports = SkillsLoader;
