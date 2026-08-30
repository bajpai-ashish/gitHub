-- ============================================================================
-- Inventory System Ordering & Delivery System
-- Complete PostgreSQL Database Schema DDL Script
-- ============================================================================

-- Create and set schema
CREATE SCHEMA IF NOT EXISTS juice_corner;
SET search_path TO juice_corner, public;

-- Drop tables if they exist (ordered to respect foreign key constraints)
DROP TABLE IF EXISTS activity_logs CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS banners CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS delivery_tracking CASCADE;
DROP TABLE IF EXISTS deliveries CASCADE;
DROP TABLE IF EXISTS refunds CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS coupon_redemptions CASCADE;
DROP TABLE IF EXISTS order_status_history CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS coupons CASCADE;
DROP TABLE IF EXISTS product_promotions CASCADE;
DROP TABLE IF EXISTS promotions CASCADE;
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS carts CASCADE;
DROP TABLE IF EXISTS ticket_messages CASCADE;
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS referrals CASCADE;
DROP TABLE IF EXISTS loyalty_transactions CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS auth_tokens CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS otp_verifications CASCADE;
DROP TABLE IF EXISTS customer_addresses CASCADE;
DROP TABLE IF EXISTS delivery_zones CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS delivery_personnel CASCADE;
DROP TABLE IF EXISTS dining_tables CASCADE;
DROP TABLE IF EXISTS stock_movements CASCADE;
DROP TABLE IF EXISTS purchase_order_items CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS product_ingredients CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS product_images CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS holidays CASCADE;
DROP TABLE IF EXISTS operating_hours CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

-- Drop enums if they exist
DROP TYPE IF EXISTS ingredient_unit CASCADE;
DROP TYPE IF EXISTS stock_movement_type CASCADE;
DROP TYPE IF EXISTS po_status CASCADE;
DROP TYPE IF EXISTS day_of_week CASCADE;
DROP TYPE IF EXISTS table_status CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS delivery_availability CASCADE;
DROP TYPE IF EXISTS order_type CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;
DROP TYPE IF EXISTS delivery_status CASCADE;
DROP TYPE IF EXISTS payment_method CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS refund_status CASCADE;
DROP TYPE IF EXISTS discount_type CASCADE;
DROP TYPE IF EXISTS otp_purpose CASCADE;
DROP TYPE IF EXISTS loyalty_txn_type CASCADE;
DROP TYPE IF EXISTS referral_status CASCADE;
DROP TYPE IF EXISTS ticket_status CASCADE;
DROP TYPE IF EXISTS ticket_priority CASCADE;
DROP TYPE IF EXISTS ticket_sender_type CASCADE;
DROP TYPE IF EXISTS notification_recipient_type CASCADE;
DROP TYPE IF EXISTS tokenable_type CASCADE;
DROP TYPE IF EXISTS setting_type CASCADE;


-- ---------- ENUMS / CUSTOM TYPES ----------

CREATE TYPE ingredient_unit AS ENUM ('kg', 'gram', 'liter', 'ml', 'piece');
CREATE TYPE stock_movement_type AS ENUM ('in', 'out', 'adjust', 'waste');
CREATE TYPE po_status AS ENUM ('draft', 'sent', 'received', 'cancelled');
CREATE TYPE day_of_week AS ENUM ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun');
CREATE TYPE table_status AS ENUM ('available', 'occupied', 'reserved');
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'staff', 'delivery');
CREATE TYPE delivery_availability AS ENUM ('available', 'busy', 'offline');
CREATE TYPE order_type AS ENUM ('dine_in', 'delivery');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'in_prep', 'ready', 'served', 'out_for_delivery', 'delivered', 'completed', 'cancelled');
CREATE TYPE delivery_status AS ENUM ('assigned', 'picked_up', 'on_way', 'delivered', 'failed');
CREATE TYPE payment_method AS ENUM ('cash', 'card', 'bkash', 'nagad', 'rocket', 'gateway');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
CREATE TYPE refund_status AS ENUM ('requested', 'approved', 'processed', 'rejected');
CREATE TYPE discount_type AS ENUM ('percent', 'fixed');
CREATE TYPE otp_purpose AS ENUM ('register', 'login', 'reset');
CREATE TYPE loyalty_txn_type AS ENUM ('earn', 'redeem', 'expire', 'adjust');
CREATE TYPE referral_status AS ENUM ('pending', 'completed');
CREATE TYPE ticket_status AS ENUM ('open', 'pending', 'resolved', 'closed');
CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high');
CREATE TYPE ticket_sender_type AS ENUM ('customer', 'staff');
CREATE TYPE notification_recipient_type AS ENUM ('customer', 'staff', 'delivery');
CREATE TYPE tokenable_type AS ENUM ('customer', 'user');
CREATE TYPE setting_type AS ENUM ('string', 'number', 'boolean', 'json');


-- ---------- TABLES ----------

-- 1. branches
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. operating_hours
CREATE TABLE operating_hours (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    day day_of_week NOT NULL,
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN DEFAULT FALSE,
    UNIQUE (branch_id, day)
);

-- 3. holidays
CREATE TABLE holidays (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    holiday_date DATE NOT NULL,
    reason VARCHAR(255),
    is_closed BOOLEAN DEFAULT TRUE
);

-- 4. categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    discounted_price DECIMAL(10,2),
    is_seasonal BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. product_images
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0
);

-- 7. ingredients
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    unit ingredient_unit NOT NULL,
    current_stock DECIMAL(10,3) DEFAULT 0.000,
    reorder_level DECIMAL(10,3) DEFAULT 0.000,
    cost_per_unit DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. product_ingredients
CREATE TABLE product_ingredients (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity DECIMAL(10,3) NOT NULL,
    unit ingredient_unit,
    UNIQUE (product_id, ingredient_id)
);

-- 9. suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. purchase_orders
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    po_number VARCHAR(100) UNIQUE NOT NULL,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    status po_status DEFAULT 'draft',
    total_amount DECIMAL(12,2),
    order_date DATE,
    expected_date DATE,
    received_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. purchase_order_items
CREATE TABLE purchase_order_items (
    id SERIAL PRIMARY KEY,
    purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2)
);

-- 12. users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. stock_movements
CREATE TABLE stock_movements (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    type stock_movement_type NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,
    reference_type VARCHAR(100),
    reference_id INTEGER,
    notes TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. dining_tables
CREATE TABLE dining_tables (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    table_number VARCHAR(50) NOT NULL,
    capacity INTEGER,
    status table_status DEFAULT 'available',
    qr_code VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE (branch_id, table_number)
);

-- 15. delivery_personnel
CREATE TABLE delivery_personnel (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(100),
    vehicle_number VARCHAR(100),
    license_number VARCHAR(100),
    availability delivery_availability DEFAULT 'offline',
    current_latitude DECIMAL(10,7),
    current_longitude DECIMAL(10,7)
);

-- 16. customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    phone_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    loyalty_balance INTEGER DEFAULT 0,
    referral_code VARCHAR(100) UNIQUE,
    referred_by INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. delivery_zones
CREATE TABLE delivery_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    min_order_amount DECIMAL(10,2) DEFAULT 0.00,
    estimated_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

-- 18. customer_addresses
CREATE TABLE customer_addresses (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES delivery_zones(id) ON DELETE SET NULL,
    label VARCHAR(100),
    recipient_name VARCHAR(255),
    recipient_phone VARCHAR(50),
    address_line VARCHAR(255) NOT NULL,
    area VARCHAR(255),
    city VARCHAR(255),
    postal_code VARCHAR(20),
    landmark VARCHAR(255),
    delivery_instructions TEXT,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 19. otp_verifications
CREATE TABLE otp_verifications (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    phone VARCHAR(50) NOT NULL,
    otp_code VARCHAR(20) NOT NULL,
    purpose otp_purpose NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 20. password_resets
CREATE TABLE password_resets (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 21. auth_tokens
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    tokenable_type tokenable_type NOT NULL,
    tokenable_id INTEGER NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_info VARCHAR(255),
    ip_address VARCHAR(50),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 22. favorites
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, product_id)
);

-- 23. reviews
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    order_id INTEGER, -- Foreign key defined later due to order dependency
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 24. loyalty_transactions
CREATE TABLE loyalty_transactions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_id INTEGER, -- Foreign key defined later due to order dependency
    type loyalty_txn_type NOT NULL,
    points INTEGER NOT NULL,
    balance_after INTEGER,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 25. referrals
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    referred_id INTEGER NOT NULL UNIQUE REFERENCES customers(id) ON DELETE CASCADE,
    status referral_status DEFAULT 'pending',
    reward_points INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 26. support_tickets
CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_id INTEGER, -- Foreign key defined later due to order dependency
    subject VARCHAR(255) NOT NULL,
    status ticket_status DEFAULT 'open',
    priority ticket_priority DEFAULT 'medium',
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 27. ticket_messages
CREATE TABLE ticket_messages (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_type ticket_sender_type NOT NULL,
    sender_id INTEGER NOT NULL, -- Polymorphic to customers.id or users.id
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 28. carts
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 29. cart_items
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    special_instructions TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cart_id, product_id)
);

-- 30. promotions
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type discount_type NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 31. product_promotions
CREATE TABLE product_promotions (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    promotion_id INTEGER NOT NULL REFERENCES promotions(id) ON DELETE CASCADE,
    UNIQUE (product_id, promotion_id)
);

-- 32. coupons
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255),
    description TEXT,
    discount_type discount_type NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    min_order_amount DECIMAL(10,2) DEFAULT 0.00,
    max_discount DECIMAL(10,2),
    usage_limit INTEGER,
    per_customer_limit INTEGER DEFAULT 1,
    used_count INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 33. orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    order_type order_type NOT NULL,
    table_id INTEGER REFERENCES dining_tables(id) ON DELETE SET NULL,
    address_id INTEGER REFERENCES customer_addresses(id) ON DELETE SET NULL,
    coupon_id INTEGER REFERENCES coupons(id) ON DELETE SET NULL,
    recipient_name VARCHAR(255),
    recipient_phone VARCHAR(50),
    address_snapshot TEXT,
    delivery_latitude DECIMAL(10,7),
    delivery_longitude DECIMAL(10,7),
    status order_status DEFAULT 'pending',
    subtotal DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    coupon_discount DECIMAL(10,2) DEFAULT 0.00,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    tax DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL,
    loyalty_earned INTEGER DEFAULT 0,
    loyalty_used INTEGER DEFAULT 0,
    notes TEXT,
    cancellation_reason TEXT,
    placed_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 34. order_items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0.00,
    subtotal DECIMAL(12,2) NOT NULL,
    special_instructions TEXT
);

-- 35. order_status_history
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status order_status NOT NULL,
    changed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 36. coupon_redemptions
CREATE TABLE coupon_redemptions (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    discount_amount DECIMAL(10,2) NOT NULL,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 37. payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    method payment_method NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_id VARCHAR(100),
    status payment_status DEFAULT 'pending',
    paid_at TIMESTAMP,
    gateway_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 38. refunds
CREATE TABLE refunds (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    payment_id INTEGER NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    reason TEXT,
    status refund_status DEFAULT 'requested',
    processed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 39. deliveries
CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    delivery_person_id INTEGER REFERENCES delivery_personnel(id) ON DELETE SET NULL,
    status delivery_status DEFAULT 'assigned',
    assigned_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    delivery_notes TEXT,
    failure_reason TEXT,
    proof_image_url VARCHAR(255)
);

-- 40. delivery_tracking
CREATE TABLE delivery_tracking (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    recorded_at TIMESTAMP NOT NULL
);

-- 41. notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    recipient_type notification_recipient_type NOT NULL,
    recipient_id INTEGER NOT NULL, -- Polymorphic to customers.id, users.id
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    read_at TIMESTAMP
);

-- 42. banners
CREATE TABLE banners (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    title VARCHAR(255),
    image_url VARCHAR(255) NOT NULL,
    link_url VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- 43. activity_logs
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 44. settings
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    type setting_type DEFAULT 'string',
    "group" VARCHAR(100),
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ---------- ADD DELAYED CYCLIC CONSTRAINTS ----------

ALTER TABLE reviews 
    ADD CONSTRAINT fk_reviews_order 
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL;

ALTER TABLE loyalty_transactions 
    ADD CONSTRAINT fk_loyalty_order 
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL;

ALTER TABLE support_tickets 
    ADD CONSTRAINT fk_support_tickets_order 
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL;


-- ---------- INDEXES (OPTIMIZED FOR QUERIES) ----------

CREATE UNIQUE INDEX idx_operating_hours_branch_day ON operating_hours (branch_id, day);
CREATE UNIQUE INDEX idx_product_ingredients_prod_ing ON product_ingredients (product_id, ingredient_id);
CREATE INDEX idx_stock_movements_ing_date ON stock_movements (ingredient_id, created_at);
CREATE INDEX idx_stock_movements_ref ON stock_movements (reference_type, reference_id);
CREATE UNIQUE INDEX idx_dining_tables_branch_num ON dining_tables (branch_id, table_number);
CREATE INDEX idx_otp_verifications_phone_purpose ON otp_verifications (phone, purpose);
CREATE UNIQUE INDEX idx_favorites_cust_prod ON favorites (customer_id, product_id);
CREATE INDEX idx_reviews_prod_approved ON reviews (product_id, is_approved);
CREATE INDEX idx_loyalty_transactions_cust_date ON loyalty_transactions (customer_id, created_at);
CREATE UNIQUE INDEX idx_referrals_referred ON referrals (referred_id);
CREATE UNIQUE INDEX idx_cart_items_cart_prod ON cart_items (cart_id, product_id);
CREATE UNIQUE INDEX idx_product_promotions_prod_promo ON product_promotions (product_id, promotion_id);
CREATE INDEX idx_coupon_redemptions_coupon_cust ON coupon_redemptions (coupon_id, customer_id);
CREATE INDEX idx_orders_cust_placed ON orders (customer_id, placed_at);
CREATE INDEX idx_orders_status_placed ON orders (status, placed_at);
CREATE INDEX idx_orders_type_placed ON orders (order_type, placed_at);
CREATE INDEX idx_orders_branch_status ON orders (branch_id, status);
CREATE INDEX idx_order_items_order ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);
CREATE INDEX idx_order_status_history_order_date ON order_status_history (order_id, created_at);
CREATE INDEX idx_payments_order ON payments (order_id);
CREATE INDEX idx_payments_txn ON payments (transaction_id);
CREATE INDEX idx_deliveries_rider_status ON deliveries (delivery_person_id, status);
CREATE INDEX idx_delivery_tracking_deliv_date ON delivery_tracking (delivery_id, recorded_at);
CREATE INDEX idx_notifications_rec_read ON notifications (recipient_type, recipient_id, is_read);
CREATE INDEX idx_activity_logs_entity ON activity_logs (entity_type, entity_id);
CREATE INDEX idx_activity_logs_user_date ON activity_logs (user_id, created_at);
