# FarmPower Marketplace - New Features

This document outlines the new features added to the FarmPower marketplace and how to use them.

## Features Added

### 1. Advanced Search and Filtering
- Full-text search across product titles and descriptions
- Filter by category, price range, condition, and brand
- Sort by price, date, and popularity
- Responsive filter UI with collapsible advanced filters

### 2. Image Upload to S3
- Secure file uploads to Supabase Storage
- Image preview and validation
- Support for multiple images per product
- Automatic image optimization

### 3. Price History Tracking
- Tracks all price changes for products
- Visual price history graph
- Shows percentage change and trend
- Accessible to all users

### 4. Favorite/Save Listings
- Users can save favorite products
- Favorites are synced across devices
- View all favorites in one place
- Quick access to saved items

## Setup Instructions

### 1. Database Setup

Run the SQL migration to create the necessary tables and functions:

```sql
\i migrations/20240619_add_marketplace_features.sql
```

### 2. Environment Variables

Make sure your environment variables are set up in your Supabase project:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # For server-side operations
```

### 3. Storage Setup

Create a new public bucket in Supabase Storage called `marketplace-images` with the following CORS policy:

```json
{
  "bucket": "marketplace-images",
  "name": "marketplace-images",
  "public": true,
  "file_size_limit": 5242880,
  "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
  "cors_rules": [
    {
      "origin": ["*"],
      "methods": ["GET", "HEAD", "POST", "PUT", "DELETE"],
      "allowed_headers": ["*"],
      "expose_headers": ["Content-Length", "X-Error"],
      "max_age_seconds": 3600
    }
  ]
}
```

## Usage

### Search and Filtering

The search and filtering is automatically available on the marketplace page. Users can:

- Type in the search box to filter by title or description
- Select a category from the dropdown
- Set minimum and maximum price ranges
- Toggle advanced filters for more options

### Image Upload

To use the image uploader in your forms:

```javascript
import { ImageUploader } from './assets/js/image-upload.js';

const uploader = new ImageUploader({
  bucketName: 'marketplace-images',
  acceptedTypes: ['image/jpeg', 'image/png', 'image/webp'],
  maxFileSize: 5 * 1024 * 1024, // 5MB
  prefix: 'products/'
});

// Example usage in a form
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  try {
    const result = await uploader.upload(file);
    console.log('File uploaded:', result.url);
  } catch (error) {
    console.error('Upload failed:', error.message);
  }
});
```

### Price History

To display price history for a product:

```javascript
import { priceTracker } from './assets/js/price-history.js';

// Render price history in a container
const container = document.getElementById('price-history-container');
priceTracker.renderPriceHistory(container, productId);

// Or get the raw data
const history = await priceTracker.getPriceHistory(productId);
```

### Favorites

To use the favorites functionality:

```javascript
import { favoritesManager, createFavoriteButton } from './assets/js/favorites.js';

// Create a favorite button
const button = createFavoriteButton(productId);
document.getElementById('favorite-container').appendChild(button);

// Check if an item is favorited
const isFavorited = favoritesManager.isFavorite(productId);

// Get all favorites
const favorites = await favoritesManager.getFavorites();
```

## Styling

All components use Tailwind CSS for styling. You can customize the look by modifying the utility classes in the HTML or adding custom styles in your CSS.

## Troubleshooting

### Images not uploading
- Check that the Supabase Storage bucket exists and is public
- Verify that the file size and type are within the allowed limits
- Check the browser console for any error messages

### Search not working
- Ensure the database functions were created successfully
- Check that the search term is being passed correctly
- Verify that the `pg_trgm` extension is enabled in your Supabase database

### Favorites not saving
- Make sure the user is logged in
- Check that the `favorites` table was created correctly
- Verify that the Row Level Security policies are set up properly

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
