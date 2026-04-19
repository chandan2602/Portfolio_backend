-- Check existing users and their roles
SELECT id, name, email, phone, role_id FROM login_details;

-- Update user with id=1 to be admin (if exists)
UPDATE login_details SET role_id = 1 WHERE id = 1;

-- Or insert a new admin user
INSERT INTO login_details (name, email, phone, role_id, visited_at)
VALUES ('Admin User', 'admin@example.com', '+919999999999', 1, NOW())
ON CONFLICT (email) DO UPDATE SET role_id = 1;

-- Verify admin exists
SELECT id, name, email, role_id FROM login_details WHERE role_id = 1;
