"""
Script to create an admin user or update existing user to admin
"""
from database import SessionLocal, LoginDetail

def create_admin(name: str, email: str, phone: str):
    """Create a new admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(LoginDetail).filter(
            (LoginDetail.email == email) | (LoginDetail.phone == phone)
        ).first()
        
        if existing:
            # Update to admin
            existing.role_id = 1
            db.commit()
            print(f"✓ Updated {existing.name} to admin (role_id=1)")
        else:
            # Create new admin
            admin = LoginDetail(
                name=name,
                email=email,
                phone=phone,
                role_id=1
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✓ Created admin user: {admin.name} (ID: {admin.id})")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


def make_user_admin(user_id: int):
    """Make an existing user an admin by ID"""
    db = SessionLocal()
    try:
        user = db.query(LoginDetail).filter(LoginDetail.id == user_id).first()
        if not user:
            print(f"✗ User with ID {user_id} not found")
            return
        
        user.role_id = 1
        db.commit()
        print(f"✓ {user.name} is now an admin (role_id=1)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Admin User Management\n")
    print("1. Create new admin")
    print("2. Make existing user admin by ID")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone (with +91): ").strip()
        create_admin(name, email, phone)
    elif choice == "2":
        user_id = int(input("User ID: ").strip())
        make_user_admin(user_id)
    else:
        print("Invalid choice")
