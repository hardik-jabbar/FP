// assets/js/image-upload.js
import { supabase } from './supabase.js';

export class ImageUploader {
  constructor(options = {}) {
    this.bucketName = options.bucketName || 'marketplace-images';
    this.acceptedTypes = options.acceptedTypes || ['image/jpeg', 'image/png', 'image/webp'];
    this.maxFileSize = options.maxFileSize || 5 * 1024 * 1024; // 5MB
    this.prefix = options.prefix || ''; // Optional folder prefix
  }

  async upload(file, path = '') {
    // Validate file type
    if (!this.acceptedTypes.includes(file.type)) {
      throw new Error(`Unsupported file type. Please upload one of: ${this.acceptedTypes.join(', ')}`);
    }

    // Validate file size
    if (file.size > this.maxFileSize) {
      throw new Error(`File is too large. Maximum size is ${this.maxFileSize / 1024 / 1024}MB`);
    }

    // Generate unique filename
    const fileExt = file.name.split('.').pop();
    const fileName = `${this.prefix}${Math.random().toString(36).substring(2, 15)}.${fileExt}`;
    const filePath = path ? `${path}/${fileName}` : fileName;

    // Upload to Supabase Storage
    const { data, error } = await supabase.storage
      .from(this.bucketName)
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false,
      });

    if (error) {
      console.error('Error uploading file:', error);
      throw error;
    }

    // Get public URL
    const { data: { publicUrl } } = supabase.storage
      .from(this.bucketName)
      .getPublicUrl(filePath);

    return {
      path: filePath,
      url: publicUrl,
      name: file.name,
      size: file.size,
      type: file.type,
    };
  }

  async delete(path) {
    const { error } = await supabase.storage
      .from(this.bucketName)
      .remove([path]);

    if (error) {
      console.error('Error deleting file:', error);
      throw error;
    }

    return true;
  }

  // Helper to create a file input element
  static createFileInput(options = {}) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = options.accept || 'image/*';
    input.multiple = options.multiple || false;
    input.style.display = 'none';
    
    if (options.capture) {
      input.capture = options.capture; // 'user' for front camera, 'environment' for back camera
    }
    
    return input;
  }

  // Helper to preview an image
  static createImagePreview(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.src = e.target.result;
        img.onload = () => resolve({
          element: img,
          url: e.target.result,
          width: img.width,
          height: img.height,
          aspectRatio: img.width / img.height,
        });
      };
      reader.readAsDataURL(file);
    });
  }
}
