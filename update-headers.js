const fs = require('fs');
const path = require('path');

// Files to exclude from processing
const EXCLUDED_FILES = [
  'components/header.html',
  'components/footer.html'
];

// Directories to exclude
const EXCLUDED_DIRS = [
  'node_modules',
  '.git',
  'dist',
  'build',
  'assets',
  'scripts',
  'styles',
  'css',
  'js',
  'images',
  'vendor'
];

// Function to process a single HTML file
function processFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Skip if already processed
    if (content.includes('id="header"') && content.includes('id="footer"')) {
      console.log(`Skipping already processed file: ${filePath}`);
      return;
    }
    
    // Add header placeholder after opening body tag
    if (!content.includes('id="header"')) {
      content = content.replace(
        /<body[^>]*>/i, 
        match => `${match}\n  <!-- Header will be loaded here -->\n  <div id="header"></div>\n  \n  <main class="flex-grow">`
      );
    }
    
    // Add footer placeholder before closing body tag
    if (!content.includes('id="footer"')) {
      content = content.replace(
        /<\/body>/i, 
        `  </main>\n  \n  <!-- Footer will be loaded here -->\n  <div id="footer"></div>\n</body>`
      );
    }
    
    // Add common scripts before closing head tag
    if (!content.includes('scripts/common.js')) {
      const commonScripts = `
  <!-- Common CSS -->
  <link rel="stylesheet" href="assets/css/marketplace.css">
  
  <!-- Common Scripts -->
  <script src="scripts/api.js" defer></script>
  <script src="scripts/cart.js" defer></script>
  <script src="scripts/common.js" defer></script>`;
      
      content = content.replace(
        /<\/head>/i, 
        `  ${commonScripts}\n</head>`
      );
    }
    
    // Update HTML class for dark mode
    content = content.replace(
      /<html[^>]*>/i, 
      match => {
        // Preserve existing classes if any
        if (match.includes('class="')) {
          return match.replace('class="', 'class="bg-dark text-light ');
        } else {
          return match.replace('>', ' class="bg-dark text-light">');
        }
      }
    );
    
    // Update body class
    content = content.replace(
      /<body[^>]*>/i, 
      match => {
        if (match.includes('class="')) {
          return match.replace('class="', 'class="min-h-screen flex flex-col ');
        } else {
          return match.replace('>', ' class="min-h-screen flex flex-col">');
        }
      }
    );
    
    // Save the updated file
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated: ${filePath}`);
    
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
  }
}

// Function to walk through directories
function walkDir(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      // Skip excluded directories
      if (!EXCLUDED_DIRS.includes(file) && !file.startsWith('.')) {
        walkDir(filePath);
      }
    } else if (file.endsWith('.html') && !EXCLUDED_FILES.includes(file)) {
      processFile(filePath);
    }
  });
}

// Start processing from the current directory
const startDir = path.join(__dirname, 'FARMPOWER');
console.log('Starting to update HTML files...');
walkDir(startDir);
console.log('Update complete!');
