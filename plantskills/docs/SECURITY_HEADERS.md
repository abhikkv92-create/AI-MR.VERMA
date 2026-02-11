# Security Headers Configuration

> Production security headers for AI KIT ecosystem.

---

## Overview

This document describes the security headers configured for production deployment of AI KIT components.

---

## Headers Implemented

| Header | Value | Purpose |
|--------|-------|---------|
| **Strict-Transport-Security** | `max-age=63072000; includeSubDomains; preload` | Force HTTPS for 2 years |
| **X-Frame-Options** | `SAMEORIGIN` | Prevent clickjacking |
| **X-Content-Type-Options** | `nosniff` | Prevent MIME sniffing |
| **X-XSS-Protection** | `1; mode=block` | Legacy XSS protection |
| **Referrer-Policy** | `origin-when-cross-origin` | Control referrer info |
| **Permissions-Policy** | `camera=(), microphone=(), geolocation=()` | Disable unused APIs |
| **Content-Security-Policy** | See below | Control resource loading |

---

## Content Security Policy (CSP)

```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data: https: blob:;
connect-src 'self' https: wss:;
frame-ancestors 'self';
```

### CSP Directives Explained

| Directive | Purpose |
|-----------|---------|
| `default-src 'self'` | Only load resources from same origin |
| `script-src` | Allow inline scripts for React hydration |
| `style-src` | Allow inline styles and Google Fonts |
| `img-src` | Allow images from any HTTPS source |
| `connect-src` | Allow API calls to any HTTPS endpoint |
| `frame-ancestors` | Prevent embedding in frames |

---

## Implementation

### Next.js (AI KIT Web)

Location: `web/next.config.ts`

```typescript
const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  // ... full config in next.config.ts
];

const nextConfig = {
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};
```

### Vite (MS Light Dashboard)

Location: `dashboard/security-headers.plugin.mjs`

To enable, add to `vite.config.mjs`:

```javascript
import { securityHeadersPlugin } from './security-headers.plugin.mjs';

export default defineConfig({
  plugins: [react(), tsconfigPaths(), securityHeadersPlugin()],
  // ...
});
```

---

## Verification

After deployment, verify headers using:

1. **Browser DevTools**: Network tab → Response Headers
2. **curl**: `curl -I https://your-domain.com`
3. **Security Scanner**: https://securityheaders.com

---

## Security Grade Target

With these headers configured, the application should achieve:
- **SecurityHeaders.com**: A+ rating
- **Mozilla Observatory**: A rating
