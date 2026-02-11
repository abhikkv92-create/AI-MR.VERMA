#!/usr/bin/env node
/**
 * MR.VERMA Local LLM Integration
 * Supports Ollama, llama.cpp, and other local LLM backends
 * Version: 2.0.0
 */

const http = require('http');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

class LocalLLMManager {
  constructor(config = {}) {
    this.config = {
      defaultProvider: config.provider || 'ollama',
      defaultModel: config.model || 'codellama',
      temperature: config.temperature || 0.7,
      maxTokens: config.maxTokens || 2048,
      ollamaUrl: config.ollamaUrl || 'http://localhost:11434',
      ...config
    };
    
    this.providers = new Map();
    this.currentProvider = null;
    this.status = 'disconnected';
    this.availableModels = [];
    
    this.initializeProviders();
  }

  initializeProviders() {
    // Ollama Provider
    this.providers.set('ollama', {
      name: 'Ollama',
      checkCommand: 'ollama --version',
      url: this.config.ollamaUrl,
      models: ['codellama', 'llama2', 'mistral', 'mixtral', 'vicuna', 'wizardcoder'],
      generate: this.generateOllama.bind(this),
      chat: this.chatOllama.bind(this),
      listModels: this.listOllamaModels.bind(this)
    });

    // LM Studio Provider (OpenAI-compatible)
    this.providers.set('lmstudio', {
      name: 'LM Studio',
      checkCommand: null, // Manual check
      url: 'http://localhost:1234/v1',
      models: ['local-model'],
      generate: this.generateOpenAICompatible.bind(this),
      chat: this.chatOpenAICompatible.bind(this),
      listModels: () => Promise.resolve(['local-model'])
    });

    // Text Generation WebUI (oobabooga)
    this.providers.set('textgen', {
      name: 'Text Generation WebUI',
      checkCommand: null,
      url: 'http://localhost:5000/v1',
      models: ['local-model'],
      generate: this.generateOpenAICompatible.bind(this),
      chat: this.chatOpenAICompatible.bind(this),
      listModels: () => Promise.resolve(['local-model'])
    });

    // llama.cpp Server
    this.providers.set('llamacpp', {
      name: 'llama.cpp',
      checkCommand: null,
      url: 'http://localhost:8080',
      models: ['local-model'],
      generate: this.generateLlamaCpp.bind(this),
      chat: this.chatLlamaCpp.bind(this),
      listModels: () => Promise.resolve(['local-model'])
    });
  }

  async initialize() {
    console.log('🧠 Initializing Local LLM Manager...');
    
    // Try to connect to default provider
    const connected = await this.connect(this.config.defaultProvider);
    
    if (!connected) {
      console.log('⚠️  Default provider not available, trying alternatives...');
      
      // Try other providers
      for (const [providerId, provider] of this.providers) {
        if (providerId !== this.config.defaultProvider) {
          const altConnected = await this.connect(providerId);
          if (altConnected) {
            console.log(`✅ Connected to ${provider.name}`);
            break;
          }
        }
      }
    }
    
    if (this.status === 'connected') {
      console.log(`✅ Local LLM ready: ${this.currentProvider.name}`);
      this.availableModels = await this.currentProvider.listModels();
      console.log(`   Models available: ${this.availableModels.length}`);
    } else {
      console.log('⚠️  No local LLM detected. Install Ollama or start your LLM server.');
      console.log('   Quick start: https://ollama.com/download');
    }
    
    return this;
  }

  async connect(providerId) {
    const provider = this.providers.get(providerId);
    if (!provider) return false;
    
    try {
      // Check if provider is running
      const isRunning = await this.checkProviderStatus(provider);
      
      if (isRunning) {
        this.currentProvider = provider;
        this.status = 'connected';
        return true;
      }
    } catch (error) {
      console.log(`   ${provider.name} not available: ${error.message}`);
    }
    
    return false;
  }

  async checkProviderStatus(provider) {
    return new Promise((resolve) => {
      // Try to connect to the provider's URL
      const url = new URL(provider.url);
      
      const req = http.request({
        hostname: url.hostname,
        port: url.port,
        path: url.pathname === '/' ? '/api/tags' : url.pathname,
        method: 'GET',
        timeout: 2000
      }, (res) => {
        resolve(res.statusCode === 200);
      });
      
      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });
      
      req.end();
    });
  }

  async generate(prompt, options = {}) {
    if (this.status !== 'connected') {
      throw new Error('No local LLM connected');
    }
    
    const model = options.model || this.config.defaultModel;
    const temperature = options.temperature || this.config.temperature;
    const maxTokens = options.maxTokens || this.config.maxTokens;
    
    console.log(`🤖 Generating with ${this.currentProvider.name} (${model})...`);
    
    return await this.currentProvider.generate(prompt, {
      model,
      temperature,
      maxTokens,
      ...options
    });
  }

  async chat(messages, options = {}) {
    if (this.status !== 'connected') {
      throw new Error('No local LLM connected');
    }
    
    const model = options.model || this.config.defaultModel;
    
    console.log(`💬 Chat with ${this.currentProvider.name} (${model})...`);
    
    return await this.currentProvider.chat(messages, {
      model,
      temperature: options.temperature || this.config.temperature,
      ...options
    });
  }

  // Ollama-specific implementations
  async generateOllama(prompt, options) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        model: options.model,
        prompt: prompt,
        stream: false,
        options: {
          temperature: options.temperature,
          num_predict: options.maxTokens
        }
      });

      const req = http.request({
        hostname: 'localhost',
        port: 11434,
        path: '/api/generate',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve({
              text: response.response,
              model: options.model,
              tokens: response.eval_count || 0,
              provider: 'ollama'
            });
          } catch (e) {
            reject(new Error('Invalid response from Ollama'));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Ollama request timeout'));
      });

      req.write(postData);
      req.end();
    });
  }

  async chatOllama(messages, options) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        model: options.model,
        messages: messages,
        stream: false,
        options: {
          temperature: options.temperature
        }
      });

      const req = http.request({
        hostname: 'localhost',
        port: 11434,
        path: '/api/chat',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve({
              message: response.message,
              model: options.model,
              tokens: response.eval_count || 0,
              provider: 'ollama'
            });
          } catch (e) {
            reject(new Error('Invalid response from Ollama'));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Ollama request timeout'));
      });

      req.write(postData);
      req.end();
    });
  }

  async listOllamaModels() {
    return new Promise((resolve, reject) => {
      const req = http.request({
        hostname: 'localhost',
        port: 11434,
        path: '/api/tags',
        method: 'GET',
        timeout: 5000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve(response.models?.map(m => m.name) || []);
          } catch (e) {
            resolve([]);
          }
        });
      });

      req.on('error', () => resolve([]));
      req.on('timeout', () => {
        req.destroy();
        resolve([]);
      });

      req.end();
    });
  }

  // OpenAI-compatible implementations (LM Studio, TextGen WebUI)
  async generateOpenAICompatible(prompt, options) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        model: options.model || 'local-model',
        prompt: prompt,
        temperature: options.temperature,
        max_tokens: options.maxTokens,
        stream: false
      });

      const url = new URL(this.currentProvider.url);
      
      const req = http.request({
        hostname: url.hostname,
        port: url.port,
        path: '/completions',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve({
              text: response.choices?.[0]?.text || response.text || '',
              model: options.model,
              provider: this.currentProvider.name.toLowerCase().replace(/\s+/g, '')
            });
          } catch (e) {
            reject(new Error(`Invalid response from ${this.currentProvider.name}`));
          }
        });
      });

      req.on('error', reject);
      req.end(postData);
    });
  }

  async chatOpenAICompatible(messages, options) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        model: options.model || 'local-model',
        messages: messages,
        temperature: options.temperature,
        stream: false
      });

      const url = new URL(this.currentProvider.url);
      
      const req = http.request({
        hostname: url.hostname,
        port: url.port,
        path: '/chat/completions',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve({
              message: response.choices?.[0]?.message || { content: '' },
              model: options.model,
              provider: this.currentProvider.name.toLowerCase().replace(/\s+/g, '')
            });
          } catch (e) {
            reject(new Error(`Invalid response from ${this.currentProvider.name}`));
          }
        });
      });

      req.on('error', reject);
      req.end(postData);
    });
  }

  // llama.cpp implementation
  async generateLlamaCpp(prompt, options) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        prompt: prompt,
        temperature: options.temperature,
        n_predict: options.maxTokens,
        stream: false
      });

      const url = new URL(this.currentProvider.url);
      
      const req = http.request({
        hostname: url.hostname,
        port: url.port,
        path: '/completion',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve({
              text: response.content || '',
              model: 'llama.cpp',
              provider: 'llamacpp'
            });
          } catch (e) {
            reject(new Error('Invalid response from llama.cpp'));
          }
        });
      });

      req.on('error', reject);
      req.end(postData);
    });
  }

  async chatLlamaCpp(messages, options) {
    // llama.cpp server uses the same endpoint for chat
    const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n') + '\nassistant:';
    const response = await this.generateLlamaCpp(prompt, options);
    return {
      message: { role: 'assistant', content: response.text },
      model: 'llama.cpp',
      provider: 'llamacpp'
    };
  }

  // Utility methods
  async pullModel(modelName) {
    if (this.currentProvider?.name === 'Ollama') {
      console.log(`📥 Pulling model: ${modelName}...`);
      return new Promise((resolve, reject) => {
        exec(`ollama pull ${modelName}`, (error, stdout, stderr) => {
          if (error) {
            reject(error);
          } else {
            console.log(`✅ Model ${modelName} ready`);
            resolve(true);
          }
        });
      });
    }
    throw new Error('Model pulling only supported for Ollama');
  }

  getStatus() {
    return {
      status: this.status,
      provider: this.currentProvider?.name || null,
      model: this.config.defaultModel,
      availableModels: this.availableModels,
      url: this.currentProvider?.url || null
    };
  }

  setModel(model) {
    this.config.defaultModel = model;
    console.log(`🔄 Model set to: ${model}`);
  }
}

module.exports = LocalLLMManager;
