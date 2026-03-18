// scripts/orchestrator.js
// Main entry point - monitors source, distributes new content, runs health checks
// Can run as a continuous daemon or be triggered per-task by OpenClaw

const { SourceMonitor } = require('./monitor');
const { Distributor } = require('./distributor');
const { HealthChecker } = require('./health');

const POLL_INTERVAL = 15 * 60 * 1000; // Check for new posts every 15 minutes
const HEALTH_CHECK_INTERVAL = 6 * 60 * 60 * 1000; // Health check every 6 hours

class Orchestrator {
  constructor() {
    this.monitor = new SourceMonitor();
    this.distributor = new Distributor();
    this.healthChecker = new HealthChecker();
    this.running = false;
  }

  async runOnce() {
    console.log(`\n[Orchestrator] Starting run at ${new Date().toISOString()}`);

    // Step 1: Check for new posts
    console.log('[Orchestrator] Step 1: Checking for new posts...');
    const newPosts = await this.monitor.checkForNewPosts();

    if (newPosts.length > 0) {
      // Step 2: Distribute new content
      console.log(`[Orchestrator] Step 2: Distributing ${newPosts.length} new post(s)...`);
      // Reload distributor to pick up new manifest entries
      this.distributor = new Distributor();
      await this.distributor.distributeAll();
    } else {
      console.log('[Orchestrator] Step 2: Skipped (no new content)');
    }

    console.log(`[Orchestrator] Run complete at ${new Date().toISOString()}`);
  }

  async runDaemon() {
    this.running = true;
    console.log('[Orchestrator] Starting daemon mode...');
    console.log(`[Orchestrator] Poll interval: ${POLL_INTERVAL / 60000} minutes`);
    console.log(`[Orchestrator] Health check interval: ${HEALTH_CHECK_INTERVAL / 3600000} hours`);

    let lastHealthCheck = 0;

    while (this.running) {
      try {
        // Run health check if due
        if (Date.now() - lastHealthCheck > HEALTH_CHECK_INTERVAL) {
          console.log('\n[Orchestrator] Running scheduled health check...');
          await this.healthChecker.checkAllAccounts();
          lastHealthCheck = Date.now();
        }

        // Check for and distribute new content
        await this.runOnce();
      } catch (e) {
        console.error('[Orchestrator] Error in main loop:', e.message);
      }

      // Wait before next poll
      console.log(`[Orchestrator] Next check in ${POLL_INTERVAL / 60000} minutes...`);
      await new Promise(r => setTimeout(r, POLL_INTERVAL));
    }
  }

  stop() {
    this.running = false;
    console.log('[Orchestrator] Stopping...');
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'once';
  const orchestrator = new Orchestrator();

  switch (command) {
    case 'daemon':
      // Handle graceful shutdown
      process.on('SIGINT', () => orchestrator.stop());
      process.on('SIGTERM', () => orchestrator.stop());
      await orchestrator.runDaemon();
      break;

    case 'once':
      await orchestrator.runOnce();
      break;

    case 'distribute':
      await orchestrator.distributor.distributeAll();
      break;

    case 'health':
      await orchestrator.healthChecker.checkAllAccounts();
      break;

    case 'monitor':
      const posts = await orchestrator.monitor.checkForNewPosts();
      console.log(`Found ${posts.length} new posts`);
      break;

    default:
      console.log('Usage: node orchestrator.js <command>');
      console.log('Commands:');
      console.log('  daemon     - Run continuously, polling for new posts');
      console.log('  once       - Single run: check + distribute');
      console.log('  distribute - Distribute any undistributed content');
      console.log('  health     - Run health check on all accounts');
      console.log('  monitor    - Check source account for new posts only');
  }
}

module.exports = { Orchestrator };

if (require.main === module) {
  main();
}
