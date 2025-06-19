// Node script to add floatingChatbot.js include to every HTML file in project
// Usage: node scripts/injectChatbot.js

const fs = require('fs');
const path = require('path');

function inject(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  if (content.includes('assets/js/floatingChatbot.js')) {
    console.log(`Already injected: ${filePath}`);
    return;
  }
  const scriptTag = '<script src="assets/js/floatingChatbot.js"></script>';
  if (content.includes('</body>')) {
    content = content.replace('</body>', `  ${scriptTag}\n</body>`);
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Injected into ${filePath}`);
  } else {
    console.warn(`No </body> tag found in ${filePath}, skipped.`);
  }
}

const SKIP_DIRS = ['assets', 'node_modules', '.git', 'models'];
function walkDir(dir) {
  fs.readdirSync(dir).forEach((file) => {
    const full = path.join(dir, file);
    if (SKIP_DIRS.some(skip => full.includes(path.sep + skip + path.sep))) return;
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      walkDir(full);
    } else if (file.endsWith('.html')) {
      inject(full);
    }
  });
}

walkDir(path.resolve(__dirname, '..'));
console.log('Chatbot injection complete.');
