from app import app, db, Product, User, bcrypt
from datetime import datetime

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Only seed if the products table is empty
        if Product.query.count() == 0:
            print("Seeding database with sample products...")
            
            # Sample products
            products = [
                {
                    'name': 'Ceramic Vase',
                    'description': 'Minimalist ceramic vase perfect for small floral arrangements or as a standalone decorative piece.',
                    'price': 49.00,
                    'image_url': 'https://images.unsplash.com/photo-1563341591-a4ef278512e0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Home Decor',
                    'inventory': 50,
                    'is_featured': True,
                    'is_new': True,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Desk Organizer',
                    'description': 'Walnut wood desk organizer with multiple compartments for stationery and office supplies.',
                    'price': 38.00,
                    'image_url': 'https://images.unsplash.com/photo-1619618651603-93f8de9b891d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Office',
                    'inventory': 75,
                    'is_featured': False,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Linen Bedding Set',
                    'description': '100% natural linen bedding set including duvet cover and two pillowcases.',
                    'price': 129.00,
                    'image_url': 'https://images.unsplash.com/photo-1567016526052-058babcd81ec?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Bedroom',
                    'inventory': 30,
                    'is_featured': True,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Coffee Mug',
                    'description': 'Handcrafted ceramic coffee mug with a natural finish.',
                    'price': 24.00,
                    'image_url': 'https://images.unsplash.com/photo-1611486212557-88be5ff6f941?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Kitchen',
                    'inventory': 100,
                    'is_featured': False,
                    'is_new': True,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Cutting Board',
                    'description': 'Acacia wood cutting board with juice groove, perfect for food preparation and serving.',
                    'price': 45.00,
                    'image_url': 'https://images.unsplash.com/photo-1616046229478-9901c5536a45?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Kitchen',
                    'inventory': 60,
                    'is_featured': False,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Scented Candle',
                    'description': '100% soy wax candle with essential oils in a glass container.',
                    'price': 25.00,
                    'image_url': 'https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Home Decor',
                    'inventory': 80,
                    'is_featured': True,
                    'is_new': False,
                    'is_sale': True,
                    'sale_price': 18.00
                },
                {
                    'name': 'Wall Mirror',
                    'description': 'Round wall mirror with brass frame, adds light and dimension to any space.',
                    'price': 89.00,
                    'image_url': 'https://images.unsplash.com/photo-1580331451062-99ff652288d7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Home Decor',
                    'inventory': 25,
                    'is_featured': False,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Throw Blanket',
                    'description': 'Soft cotton throw blanket with tassels, perfect for colder evenings.',
                    'price': 55.00,
                    'image_url': 'https://images.unsplash.com/photo-1505051508008-923feaf90180?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                    'category': 'Living Space',
                    'inventory': 40,
                    'is_featured': False,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Wool Throw Blanket',
                    'description': 'Premium wool throw blanket with a herringbone pattern, perfect for snuggling.',
                    'price': 85.00,
                    'image_url': 'https://images.unsplash.com/photo-1582655432787-e6b8809564fb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1480&q=80',
                    'category': 'Living Space',
                    'inventory': 30,
                    'is_featured': True,
                    'is_new': False,
                    'is_sale': True,
                    'sale_price': 70.00
                },
                {
                    'name': 'Linen Napkins (Set of 4)',
                    'description': 'Set of 4 natural linen napkins with hemstitch detail.',
                    'price': 28.00,
                    'image_url': 'https://images.unsplash.com/photo-1590587754549-a83eee4a8a1c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1480&q=80',
                    'category': 'Kitchen',
                    'inventory': 65,
                    'is_featured': False,
                    'is_new': True,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Ceramic Vase',
                    'description': 'Handcrafted ceramic vase with a textured finish.',
                    'price': 42.00,
                    'image_url': 'https://images.unsplash.com/photo-1616046229478-9901c5536a45?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1480&q=80',
                    'category': 'Home Decor',
                    'inventory': 35,
                    'is_featured': False,
                    'is_new': False,
                    'is_sale': False,
                    'sale_price': None
                },
                {
                    'name': 'Minimal T-shirt',
                    'description': 'Organic cotton t-shirt with a minimal design. Perfect for everyday wear.',
                    'price': 35.00,
                    'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1480&q=80',
                    'category': 'Apparel',
                    'inventory': 100,
                    'is_featured': True,
                    'is_new': True,
                    'is_sale': False,
                    'sale_price': None
                }
            ]
            
            # Add products to the database
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            # Create an admin account if there are no users
            if User.query.count() == 0:
                admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin_user = User(
                    name='Admin User',
                    email='admin@example.com',
                    password=admin_password
                )
                db.session.add(admin_user)
                print("Created admin user with email: admin@example.com and password: admin123")
            
            db.session.commit()
            print(f"Added {len(products)} products to the database")
        else:
            print("Database already contains products. Skipping seed.")

if __name__ == '__main__':
    seed_database()