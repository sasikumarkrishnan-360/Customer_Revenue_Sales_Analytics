
-- 1. Check the number of rows in each table

SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;


-- 2. Check for duplicate order IDs

SELECT order_id, COUNT(*) AS occurrences
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;


-- 3. Check for missing required values in orders

SELECT *
FROM orders
WHERE order_id IS NULL
   OR customer_id IS NULL
   OR product_id IS NULL
   OR order_date IS NULL
   OR quantity IS NULL
   OR quantity <= 0;


-- 4. Check whether order customer IDs exist

SELECT o.*
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 5. Check whether order product IDs exist

SELECT o.*
FROM orders o
LEFT JOIN products p
    ON o.product_id = p.product_id
WHERE p.product_id IS NULL;


-- 6. Check whether order employee IDs exist

SELECT o.*
FROM orders o
LEFT JOIN employees e
    ON o.employee_id = e.employee_id
WHERE o.employee_id IS NOT NULL
  AND e.employee_id IS NULL;


-- 7. Check for invalid product prices or costs

SELECT *
FROM products
WHERE cost < 0
   OR selling_price < 0;


-- 8. Check for invalid order quantities

SELECT *
FROM orders
WHERE quantity <= 0;
