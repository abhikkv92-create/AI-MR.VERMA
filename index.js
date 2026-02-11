#!/usr/bin/env node
/**
 * MR.VERMA Main Entry Point
 * Platform-agnostic initialization for OPENCODE, TRAE.AI, and Local execution
 */

const VermaStartup = require('./core/startup');

async function main() {
  const verma = new VermaStartup();
  
  try {
    const success = await verma.start();
    
    if (success) {
      // Keep process alive for platform integrations
      if (process.env.OPENCODE_ENV || process.env.TRAE_AI_ENV) {
        // Platform mode - stay alive
        process.stdin.resume();
      }
    } else {
      process.exit(1);
    }
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down MR.VERMA gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\n🛑 Shutting down MR.VERMA gracefully...');
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Run main
main();
