"""
Quick script to setup admin user
Run this after installing dependencies: pip install psycopg2-binary
"""
import psycopg2

# Database connection
DATABASE_URL = "postgresql://postgres:1234@localhost:5434/my_portfolio"

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if any users exist
    cur.execute("SELECT id, name, email, role_id FROM login_details ORDER BY id LIMIT 5;")
    users = cur.fetchall()
    
    print("Current users in database:")
    print("-" * 60)
    if users:
        for user in users:
            print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Role: {user[3]}")
    else:
        print("No users found")
    
    print("\n" + "=" * 60)
    
    # Check if user with id=1 exists
    cur.execute("SELECT id, name, email, role_id FROM login_details WHERE id = 1;")
    user_1 = cur.fetchone()
    
    if user_1:
        # Update existing user to admin
        cur.execute("UPDATE login_details SET role_id = 1 WHERE id = 1;")
        conn.commit()
        print(f"✓ Updated user ID 1 ({user_1[1]}) to admin (role_id=1)")
    else:
        # Create new admin user
        cur.execute("""
            INSERT INTO login_details (name, email, phone, role_id, visited_at)
            VALUES ('Admin User', 'admin@example.com', '+919999999999', 1, NOW())
            RETURNING id, name, email;
        """)
        new_admin = cur.fetchone()
        conn.commit()
        print(f"✓ Created new admin user: ID {new_admin[0]}, Name: {new_admin[1]}")
    
    # Show all admins
    cur.execute("SELECT id, name, email FROM login_details WHERE role_id = 1;")
    admins = cur.fetchall()
    
    print("\nAdmin users (role_id=1):")
    print("-" * 60)
    for admin in admins:
        print(f"ID: {admin[0]}, Name: {admin[1]}, Email: {admin[2]}")
    
    cur.close()
    conn.close()
    
    print("\n✓ Setup complete! You can now use any of the admin IDs above.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nMake sure:")
    print("1. PostgreSQL is running on localhost:5434")
    print("2. Database 'my_portfolio' exists")
    print("3. You have installed: pip install psycopg2-binary")
