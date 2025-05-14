import psycopg2
from decimal import Decimal

# Database connection configuration (update with your credentials)
conn = psycopg2.connect(
    dbname='dbms_project',
    user='postgres',
    password='pgadmin4',
    host='127.0.0.1',
    port='5432'  # default port for PostgreSQL
)

cursor = conn.cursor()

# Your menu data
menu_data = [
    {'id': 1, 'name': 'AI Burger', 'description': 'Juicy grilled beef patty with fresh lettuce and tomato, layered with AI-infused sauce.', 'price': Decimal('8.99'), 'image': 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=400&h=400', 'category': 'mains'},
    {'id': 2, 'name': 'Deep Learning Fries', 'description': 'Golden fried potato sticks seasoned to perfection with our recursive algorithm spice blend.', 'price': Decimal('3.49'), 'image': 'https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?q=80&w=1925&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'category': 'sides'},
    {'id': 3, 'name': 'Quantum Pizza', 'description': 'Classic pizza topped with pepperoni and mozzarella in superposition with all possible toppings.', 'price': Decimal('12.99'), 'image': 'https://images.unsplash.com/photo-1613564834361-9436948817d1?q=80&w=1943&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'category': 'mains'},
    {'id': 4, 'name': 'Machine Learning Cupcakes', 'description': 'Selection of colorful frosted cupcakes with sprinkles that adapt to your taste preferences.', 'price': Decimal('6.99'), 'image': 'https://images.unsplash.com/photo-1615832494873-b0c52d519696?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'category': 'desserts'},
    {'id': 5, 'name': 'ChatGPT Chocolate Shake', 'description': 'Creamy chocolate shake topped with whipped cream that responds to your flavor requests.', 'price': Decimal('4.99'), 'image': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=400&h=400', 'category': 'drinks'},
    {'id': 6, 'name': 'Binary Beef Sandwich', 'description': 'Crispy beef brisket with lettuce and tomato on toasted bread with a choice of 0 or 1 sauce options.', 'price': Decimal('7.99'), 'image': 'https://images.unsplash.com/photo-1619096252214-ef06c45683e3?auto=format&fit=crop&w=400&h=400', 'category': 'mains'},
    {'id': 7, 'name': 'Algorithm Avocado Toast', 'description': 'Perfectly optimized avocado spread on artisanal sourdough with optimal seasoning ratios.', 'price': Decimal('9.49'), 'image': 'https://images.unsplash.com/photo-1588137378633-dea1336ce1e2?auto=format&fit=crop&w=400&h=400', 'category': 'mains'},
    {'id': 8, 'name': 'Data Crunch Nachos', 'description': 'Crispy tortilla chips loaded with cheese and toppings, analyzed for perfect flavor distribution.', 'price': Decimal('10.99'), 'image': 'https://images.unsplash.com/photo-1582169296194-e4d644c48063?auto=format&fit=crop&w=400&h=400', 'category': 'sides'},
    {'id': 9, 'name': 'Raspberry Pi', 'description': 'Sweet raspberry filling in a buttery crust, computed to perfection with mathematical precision.', 'price': Decimal('5.99'), 'image': 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=400&h=400', 'category': 'desserts'},
    {'id': 10, 'name': 'Transformer Tacos', 'description': 'Self-attention mechanism ensures each bite has the perfect balance of flavors in every layer.', 'price': Decimal('8.49'), 'image': 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=400&h=400', 'category': 'mains'},
    {'id': 11, 'name': 'Neural Nuggets', 'description': 'Crispy chicken nuggets trained on our secret neural network of 11 herbs and spices.', 'price': Decimal('6.49'), 'image': 'https://images.unsplash.com/photo-1562967914-608f82629710?auto=format&fit=crop&w=400&h=400', 'category': 'sides'},
    {'id': 12, 'name': 'GPT-4 Garden Salad', 'description': 'Fresh vegetables intelligently arranged to generate the perfect textural response.', 'price': Decimal('7.99'), 'image': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=400&h=400', 'category': 'sides'},
    {'id': 13, 'name': 'Blockchain Burrito', 'description': 'Distributed layers of beans, rice, and cheese, each transaction of flavor securely wrapped.', 'price': Decimal('9.99'), 'image': 'https://images.unsplash.com/photo-1584208632869-05fa2b2a5934?auto=format&fit=crop&w=400&h=400', 'category': 'mains'},
    {'id': 14, 'name': 'Silicon Waffle Chips', 'description': 'Thin, crispy waffle pieces processed at high temperatures for optimal crunch factor.', 'price': Decimal('4.49'), 'image': 'https://images.unsplash.com/photo-1630953899906-d16511a72558?auto=format&fit=crop&w=400&h=400', 'category': 'sides'}
]

# Insert data into the menu_items table
insert_query = '''
INSERT INTO menu_items (id, name, description, price, image, category)
VALUES (%s, %s, %s, %s, %s, %s)
'''

for item in menu_data:
    cursor.execute(insert_query, (
        item['id'],
        item['name'],
        item['description'],
        item['price'],
        item['image'],
        item['category']
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ All data inserted into PostgreSQL 'menu_items' table successfully.")
