/**
 * Transfer Codex CR findings to Jules as fix requests
 * Posts as authenticated user (muumuu8181) so Jules picks it up
 */
import { execSync } from 'child_process';
import { writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const REPO = 'muumuu8181/ai-stress-test';

function gh(cmd) {
  try {
    return execSync(`gh ${cmd}`, { encoding: 'utf8', shell: 'bash' });
  } catch (e) {
    return null;
  }
}

function ghJson(cmd) {
  const result = gh(cmd);
  if (!result) return null;
  try { return JSON.parse(result); } catch { return null; }
}

// Get all open PRs
const prs = ghJson(`pr list --repo ${REPO} --state open --limit 50 --json number,title`);
if (!prs) { console.log('No PRs found'); process.exit(1); }

console.log(`Found ${prs.length} open PRs\n`);

let transferred = 0;
let skipped = 0;
let noFindings = 0;

for (const pr of prs) {
  // Get inline review comments
  const comments = ghJson(`api repos/muumuu8181/ai-stress-test/pulls/${pr.number}/comments`);
  if (!comments || comments.length === 0) {
    console.log(`PR #${pr.number}: No review comments, skipping`);
    noFindings++;
    continue;
  }

  // Check if we already transferred (look for @jules comment from muumuu8181)
  const issueComments = ghJson(`api repos/muumuu8181/ai-stress-test/issues/${pr.number}/comments`);
  const alreadyTransferred = issueComments && issueComments.some(c =>
    c.body.includes('@jules') && c.user.login === 'muumuu8181' &&
    c.body.includes('Codex CR')
  );

  if (alreadyTransferred) {
    console.log(`PR #${pr.number}: Already transferred, skipping`);
    skipped++;
    continue;
  }

  // Deduplicate comments (Codex sometimes posts duplicates)
  const seen = new Set();
  const uniqueComments = comments.filter(c => {
    const key = `${c.path}:${c.line}:${c.body.substring(0, 50)}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // Format findings
  const p1s = uniqueComments.filter(c => c.body.includes('P1'));
  const p2s = uniqueComments.filter(c => c.body.includes('P2') && !c.body.includes('P1'));

  if (p1s.length === 0 && p2s.length === 0) {
    console.log(`PR #${pr.number}: No P1/P2 findings, skipping`);
    noFindings++;
    continue;
  }

  // Build fix request
  let body = `@jules 以下のCodex CRレビュー指摘を修正してください。\n\n`;

  if (p1s.length > 0) {
    body += `## P1（必須修正）\n`;
    for (const c of p1s) {
      // Clean up the body (remove badge markdown)
      const cleanBody = c.body
        .replace(/\*\*<sub><sub>.*?<\/sub><\/sub>\*\*/g, '')
        .replace(/!\[.*?\]\(.*?\)/g, '')
        .trim();
      body += `- **${c.path}:${c.line}** — ${cleanBody}\n`;
    }
  }

  if (p2s.length > 0) {
    body += `\n## P2（改善推奨）\n`;
    for (const c of p2s) {
      const cleanBody = c.body
        .replace(/\*\*<sub><sub>.*?<\/sub><\/sub>\*\*/g, '')
        .replace(/!\[.*?\]\(.*?\)/g, '')
        .trim();
      body += `- **${c.path}:${c.line}** — ${cleanBody}\n`;
    }
  }

  body += `\n修正後、テストが全てパスすることを確認してください。\n`;

  // Write to temp file
  const tmpFile = join(tmpdir(), `jules-fix-${pr.number}.md`);
  writeFileSync(tmpFile, body);

  // Post comment
  const result = gh(`pr comment ${pr.number} --repo ${REPO} --body-file "${tmpFile}"`);
  if (result) {
    console.log(`PR #${pr.number}: Transferred ${p1s.length} P1 + ${p2s.length} P2 findings`);
    transferred++;
  } else {
    console.log(`PR #${pr.number}: FAILED to transfer`);
  }
}

console.log(`\n=== Summary ===`);
console.log(`Transferred: ${transferred}`);
console.log(`Already done: ${skipped}`);
console.log(`No findings: ${noFindings}`);
console.log(`Total PRs: ${prs.length}`);
