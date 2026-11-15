-- Funnel analysis on the Retailrocket events table (events.csv)
-- Columns: timestamp, visitorid, event ('view' | 'addtocart' | 'transaction'), itemid, transactionid

-- 1. Event-level funnel: how many events of each type
SELECT event, COUNT(*) AS events
FROM events
GROUP BY event
ORDER BY events DESC;

-- 2. Visitor-level funnel: how many distinct visitors reached each stage
SELECT
  COUNT(DISTINCT CASE WHEN event = 'view'        THEN visitorid END) AS viewers,
  COUNT(DISTINCT CASE WHEN event = 'addtocart'   THEN visitorid END) AS carters,
  COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS buyers
FROM events;

-- 3. Item-level funnel: of visitor-item pairs that were viewed, how many were carted and bought
WITH pairs AS (
  SELECT visitorid, itemid,
         MAX(event = 'view')        AS viewed,
         MAX(event = 'addtocart')   AS carted,
         MAX(event = 'transaction') AS bought
  FROM events
  GROUP BY visitorid, itemid
)
SELECT
  SUM(viewed)                         AS viewed_pairs,
  SUM(viewed AND carted)              AS viewed_and_carted,
  SUM(carted AND bought)              AS carted_and_bought
FROM pairs;

-- 4. Busiest hours for add-to-cart (UTC), to look for when shoppers drop off
SELECT CAST(strftime('%H', timestamp / 1000, 'unixepoch') AS INTEGER) AS hour_utc,
       SUM(event = 'view')      AS views,
       SUM(event = 'addtocart') AS carts,
       ROUND(100.0 * SUM(event = 'addtocart') / SUM(event = 'view'), 2) AS view_to_cart_pct
FROM events
GROUP BY hour_utc
ORDER BY hour_utc;
