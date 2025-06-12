const fs = require('fs');
const path = require('path');

// Function to fix logo paths in a file
function fixLogoPaths(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace all logo paths with the correct relative path
    content = content.replace(/src="\/?assets\/images\/logo\.(png|jpeg)"/g, 'src="assets/images/logo.png"');
    
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Fixed logo paths in ${filePath}`);
}

// Get all HTML files in the directory
const htmlFiles = fs.readdirSync('.')
    .filter(file => file.endsWith('.html'));

// Fix logo paths in each HTML file
htmlFiles.forEach(file => {
    fixLogoPaths(file);
});

// Also fix files in components directory
const componentsDir = path.join('.', 'components');
if (fs.existsSync(componentsDir)) {
    const componentFiles = fs.readdirSync(componentsDir)
        .filter(file => file.endsWith('.html'));
    
    componentFiles.forEach(file => {
        fixLogoPaths(path.join(componentsDir, file));
    });
}

console.log('All logo paths have been fixed!'); 