
-- Customer Revenue & Sales Analytics
-- Business analysis queries


-- 1. Overall KPIs: orders, units, revenue, cost, profit,
-- profit margin and average order value

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.quantity) AS total_units_sold,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * p.cost) AS total_cost,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit,
    ROUND(
        100.0 * SUM(o.quantity * (p.selling_price - p.cost))
        / NULLIF(SUM(o.quantity * p.selling_price), 0),
        2
    ) AS profit_margin_pct,
    ROUND(
        SUM(o.quantity * p.selling_price)::NUMERIC
        / NULLIF(COUNT(DISTINCT o.order_id), 0),
        2
    ) AS average_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;


-- 2. Revenue, cost and profit by product

SELECT
    p.product_id,
    p.product_name,
    SUM(o.quantity) AS total_quantity,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * p.cost) AS total_cost,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit,
    ROUND(
        100.0 * SUM(o.quantity * (p.selling_price - p.cost))
        / NULLIF(SUM(o.quantity * p.selling_price), 0),
        2
    ) AS profit_margin_pct
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC;


-- 3. Revenue and profit by product category

SELECT
    p.category,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * p.cost) AS total_cost,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit,
    ROUND(
        100.0 * SUM(o.quantity * (p.selling_price - p.cost))
        / NULLIF(SUM(o.quantity * p.selling_price), 0),
        2
    ) AS profit_margin_pct
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 4. Revenue and profit by customer

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.segment,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.segment
ORDER BY total_revenue DESC;


-- 5. Revenue by customer city

SELECT
    c.city,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.city
ORDER BY total_revenue DESC;


-- 6. Revenue and order count by sales channel

SELECT
    o.sales_channel,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity) AS total_quantity,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * p.cost) AS total_cost,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit,
    ROUND(
        SUM(o.quantity * p.selling_price)::NUMERIC
        / NULLIF(COUNT(DISTINCT o.order_id), 0),
        2
    ) AS average_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY o.sales_channel
ORDER BY total_revenue DESC;


-- 7. Monthly revenue, cost and profit

SELECT
    DATE_TRUNC('month', o.order_date)::DATE AS month,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity) AS total_quantity,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * p.cost) AS total_cost,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit,
    ROUND(
        100.0 * SUM(o.quantity * (p.selling_price - p.cost))
        / NULLIF(SUM(o.quantity * p.selling_price), 0),
        2
    ) AS profit_margin_pct
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;


-- 8. Monthly revenue growth percentage

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_date)::DATE AS month,
        SUM(o.quantity * p.selling_price) AS total_revenue
    FROM orders o
    JOIN products p
        ON o.product_id = p.product_id
    GROUP BY DATE_TRUNC('month', o.order_date)
),
revenue_with_previous AS (
    SELECT
        month,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY month)
            AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    month,
    total_revenue,
    previous_month_revenue,
    ROUND(
        100.0 * (total_revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS revenue_growth_pct
FROM revenue_with_previous
ORDER BY month;


-- 9. Revenue by employee

SELECT
    e.employee_id,
    e.employee_name,
    e.city AS employee_city,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit
FROM employees e
JOIN orders o
    ON e.employee_id = o.employee_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    e.employee_id,
    e.employee_name,
    e.city
ORDER BY total_revenue DESC;


-- 10. Revenue by customer segment

SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity * p.selling_price) AS total_revenue,
    SUM(o.quantity * (p.selling_price - p.cost))
        AS total_profit
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.segment
ORDER BY total_revenue DESC;


-- 11. Top five products by revenue

SELECT
    p.product_name,
    SUM(o.quantity * p.selling_price) AS total_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC
LIMIT 5;


-- 12. Orders and sales detail for investigation

SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.city AS customer_city,
    c.segment,
    p.product_name,
    p.category,
    o.quantity,
    p.selling_price,
    p.cost,
    o.quantity * p.selling_price AS total_revenue,
    o.quantity * p.cost AS total_cost,
    o.quantity * (p.selling_price - p.cost)
        AS total_profit,
    o.sales_channel,
    e.employee_name
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN products p
    ON o.product_id = p.product_id
LEFT JOIN employees e
    ON o.employee_id = e.employee_id
ORDER BY o.order_date, o.order_id;
