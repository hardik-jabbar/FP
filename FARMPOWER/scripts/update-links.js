const fs = require('fs');
const path = require('path');

// Function to walk through directory recursively
function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walkDir(dirPath, callback) : callback(path.join(dir, f));
  });
}

// Function to update links in a file
function updateLinks(filePath) {
  if (!filePath.endsWith('.html')) return;

  let content = fs.readFileSync(filePath, 'utf8');
  let isModified = false;

  // Calculate relative path to root
  const relativePath = path.relative(path.dirname(filePath), process.cwd())
    .split(path.sep)
    .join('/');

  // Replace absolute paths with relative paths
  const newContent = content.replace(/["'](\/FARMPOWER\/[^"']*?)["']/g, (match, p1) => {
    isModified = true;
    // If we're in the root directory, use ./ otherwise use the relative path
    const prefix = relativePath === '' ? './' : relativePath + '/';
    return `"${prefix}${p1.replace('/FARMPOWER/', '')}"`;
  });

  if (isModified) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    console.log(`Updated links in: ${filePath}`);
  }
}

// Start walking from the current directory
walkDir(process.cwd(), updateLinks); 