#!/usr/bin/env node
/**
 * Security-by-Design Hardening Module v1.0.0
 * ==================================================
 * Zero-trust security framework for multi-agent environments.
 *
 * Capabilities:
 *   - Identity & Access Management (IAM) with granular per-agent permissions
 *   - End-to-end encryption for data-at-rest and data-in-transit
 *   - Input sanitization & injection prevention (XSS, SQLi, command injection)
 *   - Audit logging with tamper-evident hashing
 *   - Secrets management with in-memory vault
 *   - Rate limiting per agent / per endpoint
 */

'use strict';

const crypto = require('crypto');

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const ENCRYPTION_ALGO = 'aes-256-gcm';
const KEY_LENGTH = 32; // bytes
const IV_LENGTH = 16;  // bytes
const AUTH_TAG_LENGTH = 16;
const HASH_ALGO = 'sha256';
const HMAC_ALGO = 'sha256';

// ---------------------------------------------------------------------------
// IAM - Identity & Access Management
// ---------------------------------------------------------------------------
class AgentIAM {
  constructor() {
    this._identities = new Map();   // agentId -> identity
    this._roles = new Map();        // roleName -> permissions set
    this._sessions = new Map();     // tokenHash -> session
    this._auditLog = [];

    this._initializeDefaultRoles();
  }

  _initializeDefaultRoles() {
    this._roles.set('orchestrator', new Set([
      'agent:create', 'agent:delete', 'agent:activate', 'agent:deactivate',
      'workflow:execute', 'workflow:create', 'workflow:delete',
      'skill:load', 'skill:execute',
      'system:configure', 'system:monitor',
      'data:read', 'data:write', 'data:delete',
      'secret:read'
    ]));

    this._roles.set('specialist', new Set([
      'workflow:execute',
      'skill:execute',
      'data:read', 'data:write',
      'agent:communicate'
    ]));

    this._roles.set('auditor', new Set([
      'data:read',
      'system:monitor',
      'audit:read',
      'workflow:execute',
      'skill:execute'
    ]));

    this._roles.set('viewer', new Set([
      'data:read',
      'system:monitor'
    ]));
  }

  /**
   * Register an agent identity and issue a session token.
   */
  registerAgent(agentId, role, metadata = {}) {
    const identity = {
      agentId,
      role,
      metadata,
      registeredAt: Date.now(),
      lastActivity: Date.now(),
      active: true
    };

    this._identities.set(agentId, identity);

    const token = this._issueToken(agentId, role);

    this._logAudit('AGENT_REGISTERED', agentId, { role });
    return { identity, token };
  }

  /**
   * Verify whether an agent has a specific permission.
   */
  authorize(agentId, permission) {
    const identity = this._identities.get(agentId);
    if (!identity || !identity.active) {
      this._logAudit('AUTH_DENIED', agentId, { permission, reason: 'unknown_or_inactive' });
      return false;
    }

    const rolePerms = this._roles.get(identity.role);
    if (!rolePerms || !rolePerms.has(permission)) {
      this._logAudit('AUTH_DENIED', agentId, { permission, reason: 'insufficient_role' });
      return false;
    }

    identity.lastActivity = Date.now();
    this._logAudit('AUTH_GRANTED', agentId, { permission });
    return true;
  }

  /**
   * Check whether a token is valid.
   */
  validateToken(token) {
    const hash = crypto.createHash(HASH_ALGO).update(token).digest('hex');
    const session = this._sessions.get(hash);
    if (!session) return { valid: false, reason: 'invalid_token' };
    if (session.expiresAt < Date.now()) {
      this._sessions.delete(hash);
      return { valid: false, reason: 'token_expired' };
    }
    return { valid: true, agentId: session.agentId, role: session.role };
  }

  revokeAgent(agentId) {
    const identity = this._identities.get(agentId);
    if (identity) {
      identity.active = false;
      this._logAudit('AGENT_REVOKED', agentId, {});
    }
    // Remove sessions
    for (const [hash, session] of this._sessions) {
      if (session.agentId === agentId) {
        this._sessions.delete(hash);
      }
    }
  }

  _issueToken(agentId, role) {
    const token = crypto.randomBytes(32).toString('hex');
    const hash = crypto.createHash(HASH_ALGO).update(token).digest('hex');
    this._sessions.set(hash, {
      agentId,
      role,
      issuedAt: Date.now(),
      expiresAt: Date.now() + 3600000 // 1 hour
    });
    return token;
  }

  _logAudit(event, agentId, details) {
    const entry = {
      timestamp: Date.now(),
      event,
      agentId,
      details,
      hash: null
    };
    // Chain hash for tamper evidence
    const prev = this._auditLog.length > 0
      ? this._auditLog[this._auditLog.length - 1].hash
      : '0';
    entry.hash = crypto
      .createHash(HASH_ALGO)
      .update(prev + JSON.stringify({ event, agentId, details, ts: entry.timestamp }))
      .digest('hex');

    this._auditLog.push(entry);

    // Keep bounded
    if (this._auditLog.length > 10000) {
      this._auditLog = this._auditLog.slice(-5000);
    }
  }

  getAuditLog(limit = 50) {
    return this._auditLog.slice(-limit);
  }

  getStats() {
    return {
      identities: this._identities.size,
      activeSessions: this._sessions.size,
      roles: [...this._roles.keys()],
      auditEntries: this._auditLog.length
    };
  }
}

// ---------------------------------------------------------------------------
// Encryption Engine
// ---------------------------------------------------------------------------
class EncryptionEngine {
  constructor() {
    this._masterKey = null;
    this._derivedKeys = new Map();
  }

  /**
   * Initialize with a master key. In production, source from HSM / KMS.
   */
  initialize(masterKeyHex = null) {
    if (masterKeyHex) {
      this._masterKey = Buffer.from(masterKeyHex, 'hex');
    } else {
      this._masterKey = crypto.randomBytes(KEY_LENGTH);
    }
    return this._masterKey.toString('hex');
  }

  /**
   * Derive a purpose-specific key using HKDF.
   */
  deriveKey(purpose) {
    if (this._derivedKeys.has(purpose)) {
      return this._derivedKeys.get(purpose);
    }
    const salt = crypto.createHash(HASH_ALGO).update(purpose).digest();
    const key = crypto.createHmac(HMAC_ALGO, salt).update(this._masterKey).digest();
    this._derivedKeys.set(purpose, key);
    return key;
  }

  /**
   * Encrypt plaintext using AES-256-GCM (authenticated encryption).
   */
  encrypt(plaintext, purpose = 'default') {
    const key = this.deriveKey(purpose);
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGO, key, iv, {
      authTagLength: AUTH_TAG_LENGTH
    });

    const encrypted = Buffer.concat([
      cipher.update(Buffer.from(plaintext, 'utf8')),
      cipher.final()
    ]);
    const authTag = cipher.getAuthTag();

    // Format: iv:authTag:ciphertext (all hex-encoded)
    return [
      iv.toString('hex'),
      authTag.toString('hex'),
      encrypted.toString('hex')
    ].join(':');
  }

  /**
   * Decrypt ciphertext.
   */
  decrypt(ciphertext, purpose = 'default') {
    const key = this.deriveKey(purpose);
    const [ivHex, authTagHex, encryptedHex] = ciphertext.split(':');

    const decipher = crypto.createDecipheriv(
      ENCRYPTION_ALGO,
      key,
      Buffer.from(ivHex, 'hex'),
      { authTagLength: AUTH_TAG_LENGTH }
    );
    decipher.setAuthTag(Buffer.from(authTagHex, 'hex'));

    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encryptedHex, 'hex')),
      decipher.final()
    ]);

    return decrypted.toString('utf8');
  }

  /**
   * Compute HMAC for data integrity verification.
   */
  hmac(data, purpose = 'integrity') {
    const key = this.deriveKey(purpose);
    return crypto.createHmac(HMAC_ALGO, key).update(data).digest('hex');
  }

  /**
   * Verify an HMAC.
   */
  verifyHmac(data, expectedHmac, purpose = 'integrity') {
    const computed = this.hmac(data, purpose);
    return crypto.timingSafeEqual(
      Buffer.from(computed, 'hex'),
      Buffer.from(expectedHmac, 'hex')
    );
  }
}

// ---------------------------------------------------------------------------
// Input Sanitizer - prevents injection attacks
// ---------------------------------------------------------------------------
class InputSanitizer {
  constructor() {
    this._rules = [
      {
        name: 'command_injection',
        pattern: /[;&|`$(){}[\]<>!\\]/g,
        severity: 'critical',
        action: 'strip'
      },
      {
        name: 'xss_script',
        pattern: /<script[\s>]|javascript:|on\w+\s*=/gi,
        severity: 'critical',
        action: 'reject'
      },
      {
        name: 'sql_injection',
        pattern: /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b.*\b(FROM|INTO|WHERE|TABLE|SET)\b)/gi,
        severity: 'high',
        action: 'reject'
      },
      {
        name: 'path_traversal',
        pattern: /\.\.\//g,
        severity: 'high',
        action: 'strip'
      },
      {
        name: 'null_byte',
        pattern: /\0/g,
        severity: 'critical',
        action: 'strip'
      }
    ];
  }

  /**
   * Sanitize input and return result with report.
   */
  sanitize(input, context = 'general') {
    if (typeof input !== 'string') {
      return { clean: String(input), violations: [], blocked: false };
    }

    let clean = input;
    const violations = [];
    let blocked = false;

    for (const rule of this._rules) {
      if (rule.pattern.test(clean)) {
        violations.push({
          rule: rule.name,
          severity: rule.severity,
          action: rule.action,
          context
        });

        if (rule.action === 'reject') {
          blocked = true;
          break;
        }

        if (rule.action === 'strip') {
          clean = clean.replace(rule.pattern, '');
        }
      }
      // Reset regex lastIndex for global patterns
      rule.pattern.lastIndex = 0;
    }

    return { clean: blocked ? '' : clean.trim(), violations, blocked };
  }

  /**
   * Validate that a value matches an expected format.
   */
  validateFormat(value, format) {
    const formats = {
      agentId: /^[a-z][a-z0-9_]{2,30}$/,
      workflowId: /^[a-z][a-z0-9_-]{2,50}$/,
      token: /^[a-f0-9]{64}$/,
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      semver: /^\d+\.\d+\.\d+$/,
      alphanumeric: /^[a-zA-Z0-9]+$/
    };

    const pattern = formats[format];
    if (!pattern) return { valid: false, reason: `Unknown format: ${format}` };
    return { valid: pattern.test(value), format };
  }
}

// ---------------------------------------------------------------------------
// Rate Limiter - per-agent / per-endpoint token-bucket
// ---------------------------------------------------------------------------
class RateLimiter {
  constructor() {
    this._buckets = new Map(); // key -> { tokens, lastRefill, max, refillRate }
  }

  /**
   * Configure a rate limit for a key.
   * @param {string} key - e.g. "agent:frontend_specialist" or "endpoint:/api/chat"
   * @param {number} maxTokens - max burst size
   * @param {number} refillRatePerSec - tokens added per second
   */
  configure(key, maxTokens = 60, refillRatePerSec = 10) {
    this._buckets.set(key, {
      tokens: maxTokens,
      max: maxTokens,
      refillRate: refillRatePerSec,
      lastRefill: Date.now()
    });
  }

  /**
   * Attempt to consume a token. Returns true if allowed.
   */
  allow(key, cost = 1) {
    const bucket = this._buckets.get(key);
    if (!bucket) return true; // no limit configured

    this._refill(bucket);

    if (bucket.tokens >= cost) {
      bucket.tokens -= cost;
      return true;
    }
    return false;
  }

  _refill(bucket) {
    const now = Date.now();
    const elapsed = (now - bucket.lastRefill) / 1000;
    bucket.tokens = Math.min(bucket.max, bucket.tokens + elapsed * bucket.refillRate);
    bucket.lastRefill = now;
  }

  getStats() {
    const stats = {};
    for (const [key, bucket] of this._buckets) {
      this._refill(bucket);
      stats[key] = {
        tokens: bucket.tokens.toFixed(1),
        max: bucket.max,
        refillRate: bucket.refillRate
      };
    }
    return stats;
  }
}

// ---------------------------------------------------------------------------
// Secrets Vault - in-memory encrypted secret store
// ---------------------------------------------------------------------------
class SecretsVault {
  constructor(encryption) {
    this._encryption = encryption;
    this._secrets = new Map();
  }

  set(name, value) {
    const encrypted = this._encryption.encrypt(value, 'secrets');
    this._secrets.set(name, {
      encrypted,
      setAt: Date.now(),
      accessCount: 0
    });
  }

  get(name) {
    const entry = this._secrets.get(name);
    if (!entry) return null;
    entry.accessCount++;
    return this._encryption.decrypt(entry.encrypted, 'secrets');
  }

  has(name) {
    return this._secrets.has(name);
  }

  delete(name) {
    return this._secrets.delete(name);
  }

  list() {
    return [...this._secrets.keys()];
  }
}

// ---------------------------------------------------------------------------
// SecurityHardeningModule - facade
// ---------------------------------------------------------------------------
class SecurityHardeningModule {
  constructor(config = {}) {
    this.config = config;
    this.iam = new AgentIAM();
    this.encryption = new EncryptionEngine();
    this.sanitizer = new InputSanitizer();
    this.rateLimiter = new RateLimiter();
    this.vault = null; // initialized after encryption

    this._initialized = false;
  }

  async initialize() {
    const masterKey = this.encryption.initialize(this.config.masterKeyHex || null);
    this.vault = new SecretsVault(this.encryption);

    // Configure default rate limits
    this.rateLimiter.configure('global', 1000, 100);

    this._initialized = true;
    return { masterKey, status: 'initialized' };
  }

  /**
   * Register an agent with IAM and configure rate limits.
   */
  registerAgent(agentId, role, rateLimit = { max: 60, rate: 10 }) {
    const result = this.iam.registerAgent(agentId, role);
    this.rateLimiter.configure(`agent:${agentId}`, rateLimit.max, rateLimit.rate);
    return result;
  }

  /**
   * Gate check: authorize + rate-limit + sanitize input in one call.
   */
  gate(agentId, permission, input = null) {
    // Rate limit
    if (!this.rateLimiter.allow(`agent:${agentId}`)) {
      return { allowed: false, reason: 'rate_limited' };
    }

    // Authorization
    if (!this.iam.authorize(agentId, permission)) {
      return { allowed: false, reason: 'unauthorized' };
    }

    // Input sanitization
    if (input !== null) {
      const sanitized = this.sanitizer.sanitize(input);
      if (sanitized.blocked) {
        return { allowed: false, reason: 'input_blocked', violations: sanitized.violations };
      }
      return { allowed: true, cleanInput: sanitized.clean, violations: sanitized.violations };
    }

    return { allowed: true };
  }

  getStatus() {
    return {
      initialized: this._initialized,
      iam: this.iam.getStats(),
      rateLimiter: this.rateLimiter.getStats(),
      secrets: this.vault ? this.vault.list().length : 0,
      encryption: { algorithm: ENCRYPTION_ALGO, keyLength: KEY_LENGTH * 8 }
    };
  }
}

module.exports = {
  SecurityHardeningModule,
  AgentIAM,
  EncryptionEngine,
  InputSanitizer,
  RateLimiter,
  SecretsVault
};
