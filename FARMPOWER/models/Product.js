const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please enter product name'],
    trim: true,
    maxLength: [100, 'Product name cannot exceed 100 characters']
  },
  description: {
    type: String,
    required: [true, 'Please enter product description']
  },
  price: {
    type: Number,
    required: [true, 'Please enter product price'],
    maxLength: [8, 'Price cannot exceed 8 characters'],
    default: 0.0
  },
  images: [{
    url: {
      type: String,
      required: true
    }
  }],
  category: {
    type: String,
    required: [true, 'Please select category for this product'],
    enum: {
      values: [
        'Tractors',
        'Parts',
        'Implements',
        'Service',
        'Accessories'
      ],
      message: 'Please select correct category'
    }
  },
  manufacturer: {
    type: String,
    required: [true, 'Please enter product manufacturer']
  },
  model: {
    type: String,
    required: [true, 'Please enter product model']
  },
  year: {
    type: Number,
    required: [true, 'Please enter product year']
  },
  specifications: {
    horsepower: Number,
    engineType: String,
    transmission: String,
    driveTrain: String,
    weight: Number,
    fuelType: String
  },
  stock: {
    type: Number,
    required: [true, 'Please enter product stock'],
    maxLength: [5, 'Stock cannot exceed 5 characters'],
    default: 0
  },
  warranty: {
    type: String,
    default: '1 year limited warranty'
  },
  ratings: {
    type: Number,
    default: 0
  },
  numOfReviews: {
    type: Number,
    default: 0
  },
  reviews: [
    {
      user: {
        type: mongoose.Schema.ObjectId,
        ref: 'User',
        required: true
      },
      name: {
        type: String,
        required: true
      },
      rating: {
        type: Number,
        required: true
      },
      comment: {
        type: String,
        required: true
      },
      createdAt: {
        type: Date,
        default: Date.now
      }
    }
  ],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Product', productSchema); 