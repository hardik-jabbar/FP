// Link Checker Script
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// Configuration
const config = {
  baseDir: path.resolve(__dirname, '..'),
  validExtensions: ['.html', '.htm'],
  excludeDirs: ['node_modules', '.git', 'assets'],
  baseUrl: '/FARMPOWER',
  requiredPages: [
    'index.html',
    'shop.html',
    'parts-marketplace.html',
    'service-scheduling.html',
    'gps-tracking.html',
    'crop-calculator.html',
    'notifications.html',
    'profile.html',
    'my-equipment.html',
    'my-services.html',
    'settings.html',
    'login.html',
    'register.html',
    'help-center.html',
    'faq.html',
    'contact.html',
    'terms.html',
    'privacy.html'
  ]
};

// Store all found links
const links = new Set();
const files = new Set();
const brokenLinks = new Set();
const missingPages = new Set();

// Helper function to check if a file exists
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (err) {
    return false;
  }
}

// Helper function to normalize a link
function normalizeLink(link) {
  // Remove hash and query parameters
  link = link.split('#')[0].split('?')[0];
  
  // Remove trailing slash
  if (link.endsWith('/')) {
    link = link.slice(0, -1);
  }
  
  // Add .html extension if no extension
  if (!path.extname(link) && !link.includes('.')) {
    link = `${link}.html`;
  }
  
  return link;
}

// Function to scan a file for links
function scanFileForLinks(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const $ = cheerio.load(content);
    
    // Find all links
    $('a').each((_, element) => {
      const href = $(element).attr('href');
      if (href && !href.startsWith('http') && !href.startsWith('mailto:')) {
        const normalizedLink = normalizeLink(href);
        links.add(normalizedLink);
        
        // Check if link is valid
        const targetPath = path.join(config.baseDir, normalizedLink.replace(config.baseUrl, ''));
        if (!fileExists(targetPath)) {
          brokenLinks.add({
            source: filePath,
            link: href,
            normalizedLink
          });
        }
      }
    });
  } catch (err) {
    console.error(`Error scanning file ${filePath}:`, err);
  }
}

// Function to walk directory and find HTML files
function walkDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      if (!config.excludeDirs.includes(entry.name)) {
        walkDir(fullPath);
      }
    } else if (config.validExtensions.includes(path.extname(entry.name).toLowerCase())) {
      files.add(fullPath);
      scanFileForLinks(fullPath);
    }
  }
}

// Check for missing required pages
function checkRequiredPages() {
  for (const page of config.requiredPages) {
    const pagePath = path.join(config.baseDir, page);
    if (!fileExists(pagePath)) {
      missingPages.add(page);
    }
  }
}

// Main execution
console.log('Starting link checker...\n');

// Scan all files
walkDir(config.baseDir);

// Check required pages
checkRequiredPages();

// Report results
console.log('=== Link Checker Report ===\n');

console.log('Files scanned:', files.size);
console.log('Unique links found:', links.size);
console.log('Broken links found:', brokenLinks.size);
console.log('Missing required pages:', missingPages.size);

if (brokenLinks.size > 0) {
  console.log('\nBroken Links:');
  brokenLinks.forEach(({ source, link, normalizedLink }) => {
    console.log(`\nSource: ${path.relative(config.baseDir, source)}`);
    console.log(`Link: ${link}`);
    console.log(`Normalized: ${normalizedLink}`);
  });
}

if (missingPages.size > 0) {
  console.log('\nMissing Required Pages:');
  missingPages.forEach(page => {
    console.log(`- ${page}`);
  });
}

// Create missing pages
if (missingPages.size > 0) {
  console.log('\nCreating missing pages...');
  
  for (const page of missingPages) {
    const pagePath = path.join(config.baseDir, page);
    const pageDir = path.dirname(pagePath);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(pageDir)) {
      fs.mkdirSync(pageDir, { recursive: true });
    }
    
    // Create basic page template
    const pageTitle = page.replace('.html', '').split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
    
    const template = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${pageTitle} - FarmPower</title>
  <meta name="description" content="${pageTitle} page of FarmPower - Your smart farming platform">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-background text-foreground">
  <!-- Include Header -->
  <div id="header-placeholder"></div>

  <main class="container mx-auto px-4 md:px-6 py-8">
    <h1 class="text-3xl font-bold mb-4">${pageTitle}</h1>
    <p class="text-muted-foreground">Content coming soon...</p>
  </main>

  <!-- Include Footer -->
  <div id="footer-placeholder"></div>

  <script>
    // Load header and footer
    fetch('/FARMPOWER/components/header.html')
      .then(response => response.text())
      .then(data => {
        document.getElementById('header-placeholder').innerHTML = data;
      });

    fetch('/FARMPOWER/components/footer.html')
      .then(response => response.text())
      .then(data => {
        document.getElementById('footer-placeholder').innerHTML = data;
      });
  </script>
</body>
</html>`;
    
    fs.writeFileSync(pagePath, template);
    console.log(`Created: ${page}`);
  }
}

console.log('\nLink checker completed!'); 