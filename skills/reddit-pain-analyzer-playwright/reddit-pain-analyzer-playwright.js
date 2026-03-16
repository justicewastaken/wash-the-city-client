#!/usr/bin/env node
/**
 * Reddit Pain Analyzer (Playwright Stealth Version)
 * Scrapes Reddit with anti-bot protection, analyzes pain points.
 * 
 * Usage: node reddit-pain-analyzer-playwright.js <subreddit> [days_back=180] [min_comments=3]
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
};

const PAIN_KEYWORDS = {
    'time_management': ['hours', 'week', 'time', 'manual', 'automate', 'automatic', 'waste', 'spending', 'takes', 'efficiency'],
    'money_loss': ['losing', 'lost', 'cost', 'expensive', 'fee', 'fine', 'penalty', 'revenue', 'money', 'profit'],
    'frustration': ['frustrated', 'annoying', 'hate', 'sucks', 'nightmare', 'pain', 'struggle', 'difficult', 'stress'],
    'scattered': ['everywhere', 'lost', 'disorganized', 'mess', 'chaos', 'hard to find', 'track'],
    'follow_up': ['follow up', 'follow-up', 'chasing', 'reminder', 'forget', 'slipping through', 'missed'],
    'paperwork': ['forms', 'paperwork', 'documents', 'records', 'files', 'HIPAA', 'consent', 'signature'],
    'appointments': ['no-show', 'no show', 'cancellation', 'late', 'reschedule', 'booking', 'schedule'],
    'insurance': ['insurance', 'claims', 'verification', 'benefits', 'eligibility', 'preauthorization'],
    'communication': ['call', 'email', 'text', 'SMS', 'notification', 'message', 'reminder'],
};

function getTimestampDaysAgo(days) {
    return Math.floor((Date.now() - days * 24 * 60 * 60 * 1000) / 1000);
}

async function scrapeSubredditWithPlaywright(subreddit, daysBack = 180, minComments = 3, maxPosts = 200) {
    console.log(`🕷️  Scraping r/${subreddit} via Playwright Stealth...`);
    
    const afterTimestamp = getTimestampDaysAgo(daysBack);
    const posts = [];
    
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
        ],
    });
    
    const context = await browser.newContext({
        userAgent: HEADERS['User-Agent'],
        viewport: { width: 375, height: 812 },
        locale: 'en-US',
    });
    
    // Hide webdriver
    await context.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        window.chrome = { runtime: {} };
    });
    
    const page = await context.newPage();
    
    try {
        // Use Reddit's search API endpoint directly
        const searchUrl = `https://www.reddit.com/r/${subreddit}/search.json?q=&restrict_sr=on&sort=new&limit=100&t=all`;
        console.log(`📡  Navigating to: ${searchUrl}`);
        
        const response = await page.goto(searchUrl, {
            waitUntil: 'domcontentloaded',
            timeout: 30000,
        });
        
        console.log(`📡 HTTP Status: ${response.status()}`);
        
        if (response.status() === 403 || response.status() === 429) {
            console.log('⚠️  Rate limited / blocked. Trying with longer wait...');
            await page.waitForTimeout(10000);
        }
        
        // Wait for JSON to load
        await page.waitForTimeout(3000);
        
        // Extract JSON from page
        const jsonData = await page.evaluate(() => {
            try {
                return JSON.parse(document.body.innerText);
            } catch (e) {
                console.error('Failed to parse JSON:', e);
                return null;
            }
        });
        
        if (!jsonData || !jsonData.data || !jsonData.data.children) {
            console.error('❌ Invalid Reddit response structure');
            fs.writeFileSync(`debug_${subreddit}.html`, await page.content());
            return [];
        }
        
        const children = jsonData.data.children;
        console.log(`📦 Found ${children.length} posts in JSON response`);
        
        for (const child of children) {
            const post = child.data;
            const created = post.created_utc;
            
            if (created < afterTimestamp) {
                continue; // Too old
            }
            
            if (post.num_comments >= minComments) {
                posts.push({
                    title: post.title,
                    selftext: post.get('selftext', ''),
                    num_comments: post.num_comments,
                    score: post.get('score', 0),
                    upvote_ratio: post.get('upvote_ratio', 0.0),
                    permalink: post.permalink,
                    created_utc: created,
                    subreddit: subreddit
                });
            }
        }
        
        console.log(`✅ Collected ${posts.length} posts from r/${subreddit}`);
        
    } catch (error) {
        console.error('❌ Scraping error:', error.message);
        fs.writeFileSync(`error_${subreddit}.html`, await page.content());
    } finally {
        await browser.close();
    }
    
    return posts;
}

function extractPainPoints(text) {
    const textLower = text.toLowerCase();
    const matches = [];
    
    for (const [category, keywords] of Object.entries(PAIN_KEYWORDS)) {
        for (const kw of keywords) {
            if (textLower.includes(kw)) {
                matches.push(category);
                break;
            }
        }
    }
    
    return matches;
}

function calculateEngagement(post) {
    const score = post.score || 0;
    const comments = post.num_comments || 0;
    return score + Math.floor(comments * 0.5);
}

function analyzePosts(posts) {
    console.log('\n📊 Analyzing posts for pain points...');
    
    const painCounter = new Map();
    const painEngagement = new Map();
    const painExamples = new Map();
    
    for (const post of posts) {
        const fullText = post.title + ' ' + post.selftext;
        const pains = extractPainPoints(fullText);
        const engagement = calculateEngagement(post);
        
        if (pains.length > 0) {
            for (const pain of pains) {
                painCounter.set(pain, (painCounter.get(pain) || 0) + 1);
                painEngagement.set(pain, (painEngagement.get(pain) || 0) + engagement);
                
                if (!painExamples.has(pain)) {
                    painExamples.set(pain, []);
                }
                painExamples.get(pain).push({
                    title: post.title,
                    score: post.score,
                    comments: post.num_comments,
                    engagement: engagement,
                    permalink: post.permalink
                });
            }
        }
    }
    
    // Sort examples by engagement descending
    for (const [pain, examples] of painExamples) {
        examples.sort((a, b) => b.engagement - a.engagement);
        painExamples.set(pain, examples.slice(0, 3));
    }
    
    // Rank by total engagement
    const rankedPains = Array.from(painEngagement.entries())
        .sort((a, b) => b[1] - a[1]);
    
    return {
        totalPosts: posts.length,
        totalWithPain: Array.from(painCounter.values()).reduce((a, b) => a + b, 0),
        painDistribution: Array.from(painCounter.entries()).sort((a, b) => b[1] - a[1]),
        painEngagement: Array.from(painEngagement.entries()).sort((a, b) => b[1] - a[1]),
        rankedByEngagement: rankedPains,
        painExamples: Object.fromEntries(painExamples),
        rawPosts: posts.slice(0, 50)
    };
}

async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.log('Usage: node reddit-pain-analyzer-playwright.js <subreddit> [days_back=180] [min_comments=3]');
        console.log('Example: node reddit-pain-analyzer-playwright.js dentistry 180 5');
        process.exit(0);
    }
    
    const subreddit = args[0];
    const daysBack = parseInt(args[1]) || 180;
    const minComments = parseInt(args[2]) || 3;
    
    const posts = await scrapeSubredditWithPlaywright(subreddit, daysBack, minComments);
    
    if (posts.length === 0) {
        console.log('No posts collected. Exiting.');
        process.exit(0);
    }
    
    const analysis = analyzePosts(posts);
    
    // Save full results
    const filename = `${subreddit}_pain_analysis_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '_')}.json`;
    fs.writeFileSync(filename, JSON.stringify(analysis, null, 2));
    console.log(`\n💾 Full results saved to: ${filename}`);
    
    // Print summary
    console.log('\n' + '='.repeat(70));
    console.log(`PAIN CLUSTER REPORT: r/${subreddit}`);
    console.log('='.repeat(70));
    console.log(`Total posts analyzed: ${analysis.totalPosts}`);
    console.log(`Posts with detected pain points: ${analysis.totalWithPain}`);
    console.log('\nTop Pain Clusters (ranked by total engagement):');
    console.log('-'.repeat(70));
    
    for (const [pain, engagement] of analysis.rankedByEngagement.slice(0, 10)) {
        const count = analysis.painDistribution.find(([p]) => p === pain)?.[1] || 0;
        console.log(`\n${pain.toUpperCase().replace('_', ' ')}: ${count} posts (total engagement: ${engagement.toLocaleString()})`);
        
        const examples = analysis.painExamples[pain];
        if (examples) {
            for (const ex of examples.slice(0, 2)) {
                console.log(`  • "${ex.title.substring(0, 80)}..."`);
                console.log(`    Score: ${ex.score.toLocaleString()} • Comments: ${ex.comments} • Engagement: ${ex.engagement.toLocaleString()}`);
                console.log(`    https://reddit.com${ex.permalink}`);
            }
        }
    }
    
    console.log('\n' + '='.repeat(70));
    console.log('Next steps:');
    console.log('1. Review the JSON file for all examples');
    console.log('2. Pick the top 2-3 pain points with clearest automation fit');
    console.log('3. Build a guide targeting that specific pain');
    console.log('4. Email businesses in that niche with your solution');
}

main().catch(err => {
    console.error('❌ Fatal error:', err);
    process.exit(1);
});
