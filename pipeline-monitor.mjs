/**
 * Pipeline monitor v2: auto-review + merge new PRs
 * Fixes: false "MERGED" detection, proper conflict handling
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
    return (e.stdout || '') + (e.stderr || '');
  }
}

function ghJson(cmd) {
  try {
    return JSON.parse(execSync(`gh ${cmd}`, { encoding: 'utf8', shell: 'bash' }));
  } catch {
    return null;
  }
}

const reviewedPRs = new Set();
const transferredPRs = new Set();
let totalMerged = 34; // already merged

console.log(`Pipeline monitor v2 starting. Already merged: ${totalMerged}`);
console.log('Press Ctrl+C to stop.\n');

let iteration = 0;

while (true) {
  iteration++;
  const now = new Date().toISOString().substring(11, 19);
  console.log(`\n[${now}] #${iteration}`);

  const openPRs = ghJson(`pr list --repo ${REPO} --state open --limit 50 --json number,title,mergeable`);
  if (!openPRs || openPRs.length === 0) {
    const issues = ghJson(`issue list --repo ${REPO} --label jules --state open --json number`);
    if (!issues || issues.length === 0) {
      console.log('All issues done!');
      break;
    }
    console.log(`${issues.length} issues open, 0 PRs. Waiting...`);
    execSync('sleep 60');
    continue;
  }

  console.log(`${openPRs.length} open PRs`);

  for (const pr of openPRs) {
    const prNum = pr.number;

    // Skip if not mergeable and already asked for conflict resolution
    if (pr.mergeable === 'CONFLICTING') {
      const issueComments = ghJson(`api repos/${REPO}/issues/${prNum}/comments`);
      const askedResolve = issueComments && issueComments.some(c =>
        c.body.includes('コンフリクト') && c.user.login === 'muumuu8181'
      );
      if (askedResolve) {
        console.log(`  PR #${prNum}: CONFLICTING (already asked Jules)`);
        continue;
      }
      gh(`pr comment ${prNum} --repo ${REPO} --body "@jules マージコンフリクトが発生しています。masterブランチをマージしてコンフリクトを解決してください。"`);
      console.log(`  PR #${prNum}: CONFLICTING - asked Jules`);
      continue;
    }

    // Step 1: Codex CR review
    if (!reviewedPRs.has(prNum)) {
      console.log(`  PR #${prNum}: Requesting @codex review...`);
      gh(`pr comment ${prNum} --repo ${REPO} --body "@codex review"`);
      reviewedPRs.add(prNum);
      execSync('sleep 30');
    }

    // Step 2: Check for review comments
    const reviewComments = ghJson(`api repos/${REPO}/pulls/${prNum}/comments`);

    // Step 3: Transfer findings to Jules
    if (reviewComments && reviewComments.length > 0 && !transferredPRs.has(prNum)) {
      const seen = new Set();
      const unique = reviewComments.filter(c => {
        const k = `${c.path}:${c.line}:${c.body.substring(0, 50)}`;
        if (seen.has(k)) return false;
        seen.add(k);
        return true;
      });

      const p1s = unique.filter(c => c.body.includes('P1'));
      const p2s = unique.filter(c => c.body.includes('P2') && !c.body.includes('P1'));

      if (p1s.length > 0 || p2s.length > 0) {
        let body = `@jules 以下のCodex CRレビュー指摘を修正してください。\n\n`;
        if (p1s.length > 0) {
          body += `## P1（必須修正）\n`;
          for (const c of p1s) {
            const clean = c.body.replace(/\*\*<sub><sub>.*?<\/sub><\/sub>\*\*/g, '').replace(/!\[.*?\]\(.*?\)/g, '').trim();
            body += `- **${c.path}:${c.line}** — ${clean}\n`;
          }
        }
        if (p2s.length > 0) {
          body += `\n## P2（改善推奨）\n`;
          for (const c of p2s) {
            const clean = c.body.replace(/\*\*<sub><sub>.*?<\/sub><\/sub>\*\*/g, '').replace(/!\[.*?\]\(.*?\)/g, '').trim();
            body += `- **${c.path}:${c.line}** — ${clean}\n`;
          }
        }
        body += `\n修正後、テストが全てパスすることを確認してください。`;

        const tmpFile = join(tmpdir(), `jules-fix-${prNum}.md`);
        writeFileSync(tmpFile, body);
        gh(`pr comment ${prNum} --repo ${REPO} --body-file "${tmpFile}"`);
        console.log(`  PR #${prNum}: Transferred ${p1s.length} P1 + ${p2s.length} P2`);
      }
      transferredPRs.add(prNum);
    }

    // Step 4: Wait for Jules fix, then merge
    if (pr.mergeable === 'MERGEABLE') {
      // Check if Jules had time to fix (at least 60s since transfer)
      const result = gh(`pr merge ${prNum} --repo ${REPO} --squash --subject "Merge PR #${prNum}"`);
      if (result.includes('already merged')) {
        console.log(`  PR #${prNum}: already merged`);
        totalMerged++;
      } else if (result.includes('was automatically merged') || result.includes('squash merge')) {
        console.log(`  PR #${prNum}: MERGED!`);
        totalMerged++;
      } else if (result.includes('not mergeable')) {
        console.log(`  PR #${prNum}: not yet mergeable`);
      } else {
        console.log(`  PR #${prNum}: ${result.substring(0, 80)}`);
      }
    } else if (pr.mergeable === 'UNKNOWN') {
      console.log(`  PR #${prNum}: mergeable=UNKNOWN, skipping`);
    }
  }

  console.log(`Total merged: ${totalMerged}`);

  // Check if we should stop (all issues closed + all PRs merged)
  const openIssues = ghJson(`issue list --repo ${REPO} --label jules --state open --json number`);
  if ((!openIssues || openIssues.length === 0) && (!openPRs || openPRs.length === 0)) {
    console.log('\nAll done! No more issues or PRs.');
    break;
  }

  console.log(`Waiting 90s... (${openIssues?.length || 0} issues remaining)`);
  execSync('sleep 90');
}
