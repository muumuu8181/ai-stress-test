import { execSync } from 'child_process';
import { writeFileSync, readFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join } from 'path';

const REPO = 'muumuu8181/ai-stress-test';

// 1. Load PR data
const prData = JSON.parse(readFileSync('report-data.json', 'utf8'));

// 2. Load quality data (from the previous analysis output)
const qualityData = {};
const dirs = readdirSync('components').filter(d => {
  try { return statSync(join('components', d)).isDirectory() && d !== '__pycache__'; } catch { return false; }
});

for (const dir of dirs) {
  const base = join('components', dir);
  const allFiles = [];
  function walk(p) {
    try {
      for (const f of readdirSync(p)) {
        const fp = join(p, f);
        if (statSync(fp).isDirectory() && f !== '__pycache__' && f !== 'node_modules') walk(fp);
        else if (f.endsWith('.py') || f.endsWith('.ts')) allFiles.push(fp);
      }
    } catch {}
  }
  walk(base);

  const srcFiles = allFiles.filter(f => !f.includes('test'));
  const testFiles = allFiles.filter(f => f.includes('test'));

  let srcLines = 0, testLines = 0, typeHints = 0, docstrings = 0, errorHandling = 0;
  for (const f of allFiles) {
    try {
      const content = readFileSync(f, 'utf8');
      const lines = content.split('\n');
      const isTest = f.includes('test');
      if (isTest) testLines += lines.length;
      else srcLines += lines.length;

      typeHints += (content.match(/def\s+\w+\([^)]*:\s*\w/g) || []).length;
      typeHints += (content.match(/->\s*\w/g) || []).length;
      docstrings += Math.floor((content.match(/"""/g) || []).length / 2);
      errorHandling += (content.match(/raise\s+\w|except\s+\w|try:/g) || []).length;
    } catch {}
  }

  qualityData[dir] = { srcFiles: srcFiles.length, testFiles: testFiles.length, srcLines, testLines, typeHints, docstrings, errorHandling };
}

// 3. Match PRs to components
const prs = prData.prs.map(pr => {
  const title = pr.title;
  // Extract component number from title
  const numMatch = title.match(/\[?0?(\d{2,3})-[\w-]+\]?/);
  const num = numMatch ? numMatch[1].padStart(3, '0') : null;

  let qData = null;
  if (num) {
    for (const [k, v] of Object.entries(qualityData)) {
      if (k.startsWith(num) || k.includes(num)) {
        qData = { component: k, ...v };
        break;
      }
    }
  }
  // Fallback: try matching by name
  if (!qData) {
    for (const [k, v] of Object.entries(qualityData)) {
      const kNorm = k.replace(/_/g, '-').toLowerCase();
      if (title.toLowerCase().includes(kNorm)) {
        qData = { component: k, ...v };
        break;
      }
    }
  }

  return {
    number: pr.number,
    component: qData ? qData.component : title.substring(0, 30),
    srcFiles: qData?.srcFiles || 0,
    testFiles: qData?.testFiles || 0,
    srcLines: qData?.srcLines || pr.additions,
    testLines: qData?.testLines || 0,
    typeHints: qData?.typeHints || 0,
    docstrings: qData?.docstrings || 0,
    errorHandling: qData?.errorHandling || 0,
    p1: pr.p1,
    p2: pr.p2
  };
});

// 4. Inject into HTML
let html = readFileSync('docs/dashboard.html', 'utf8');
html = html.replace('PR_DATA', JSON.stringify(prs));
html = html.replace('REMAIN_DATA', JSON.stringify(prData.remaining));
writeFileSync('docs/dashboard.html', html);

console.log(`Dashboard updated: ${prs.length} PRs, ${Object.keys(qualityData).length} components`);
console.log(`Sample: ${JSON.stringify(prs[0])}`);
