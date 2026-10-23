import random
import uuid
from datetime import date, timedelta

CARRIERS = ["SwiftLogistics", "GlobalFreight", "ExpressLine", "OceanBridge", "SkyCargo"]
CARRIER_BASE_DELAY = {
    "SwiftLogistics": 0.06, "GlobalFreight": 0.13, "ExpressLine": 0.09,
    "OceanBridge": 0.19, "SkyCargo": 0.07,
}
PRIORITIES = ["Standard", "Express", "Critical"]

COUNTRIES = [
    {"name": "United States", "code": "US", "continent": "North America",
     "center": [-98.5, 39.8], "zoom": 3.5, "mod": 1.00, "weight": 18,
     "cities": [
         {"name": "Los Angeles", "lon": -118.2, "lat": 34.0, "weight": 4},
         {"name": "New York", "lon": -74.0, "lat": 40.7, "weight": 3},
         {"name": "Chicago", "lon": -87.6, "lat": 41.9, "weight": 2},
         {"name": "Houston", "lon": -95.4, "lat": 29.8, "weight": 2},
         {"name": "Seattle", "lon": -122.3, "lat": 47.6, "weight": 1},
         {"name": "Miami", "lon": -80.2, "lat": 25.8, "weight": 1},
     ]},
    {"name": "Canada", "code": "CA", "continent": "North America",
     "center": [-106.3, 56.1], "zoom": 3.0, "mod": 1.05, "weight": 6,
     "cities": [
         {"name": "Toronto", "lon": -79.4, "lat": 43.7, "weight": 3},
         {"name": "Vancouver", "lon": -123.1, "lat": 49.3, "weight": 2},
         {"name": "Montreal", "lon": -73.6, "lat": 45.5, "weight": 2},
         {"name": "Calgary", "lon": -114.1, "lat": 51.0, "weight": 1},
     ]},
    {"name": "Mexico", "code": "MX", "continent": "North America",
     "center": [-102.5, 23.6], "zoom": 3.5, "mod": 1.15, "weight": 4,
     "cities": [
         {"name": "Mexico City", "lon": -99.1, "lat": 19.4, "weight": 3},
         {"name": "Guadalajara", "lon": -103.3, "lat": 20.7, "weight": 2},
         {"name": "Monterrey", "lon": -100.3, "lat": 25.7, "weight": 2},
     ]},
    {"name": "China", "code": "CN", "continent": "Asia",
     "center": [104.2, 35.9], "zoom": 3.5, "mod": 0.80, "weight": 20,
     "cities": [
         {"name": "Shanghai", "lon": 121.5, "lat": 31.2, "weight": 5},
         {"name": "Shenzhen", "lon": 114.1, "lat": 22.5, "weight": 4},
         {"name": "Guangzhou", "lon": 113.3, "lat": 23.1, "weight": 3},
         {"name": "Ningbo", "lon": 121.5, "lat": 29.9, "weight": 3},
         {"name": "Qingdao", "lon": 120.4, "lat": 36.1, "weight": 2},
         {"name": "Tianjin", "lon": 117.2, "lat": 39.1, "weight": 2},
     ]},
    {"name": "Japan", "code": "JP", "continent": "Asia",
     "center": [138.3, 36.2], "zoom": 4.0, "mod": 0.70, "weight": 7,
     "cities": [
         {"name": "Tokyo", "lon": 139.7, "lat": 35.7, "weight": 3},
         {"name": "Yokohama", "lon": 139.6, "lat": 35.4, "weight": 2},
         {"name": "Osaka", "lon": 135.5, "lat": 34.7, "weight": 2},
     ]},
    {"name": "South Korea", "code": "KR", "continent": "Asia",
     "center": [127.8, 35.9], "zoom": 5.0, "mod": 0.80, "weight": 6,
     "cities": [
         {"name": "Busan", "lon": 129.1, "lat": 35.2, "weight": 3},
         {"name": "Seoul", "lon": 126.9, "lat": 37.6, "weight": 3},
         {"name": "Incheon", "lon": 126.7, "lat": 37.5, "weight": 2},
     ]},
    {"name": "Singapore", "code": "SG", "continent": "Asia",
     "center": [103.8, 1.35], "zoom": 8.0, "mod": 0.50, "weight": 8,
     "cities": [{"name": "Singapore", "lon": 103.8, "lat": 1.35, "weight": 1}]},
    {"name": "Vietnam", "code": "VN", "continent": "Asia",
     "center": [108.3, 14.1], "zoom": 4.0, "mod": 1.10, "weight": 4,
     "cities": [
         {"name": "Ho Chi Minh", "lon": 106.7, "lat": 10.8, "weight": 3},
         {"name": "Hanoi", "lon": 105.8, "lat": 21.0, "weight": 2},
         {"name": "Haiphong", "lon": 106.7, "lat": 20.9, "weight": 1},
     ]},
    {"name": "India", "code": "IN", "continent": "Asia",
     "center": [78.9, 20.6], "zoom": 3.5, "mod": 1.25, "weight": 5,
     "cities": [
         {"name": "Mumbai", "lon": 72.9, "lat": 19.1, "weight": 3},
         {"name": "Delhi", "lon": 77.2, "lat": 28.6, "weight": 2},
         {"name": "Chennai", "lon": 80.3, "lat": 13.1, "weight": 2},
     ]},
    {"name": "Germany", "code": "DE", "continent": "Europe",
     "center": [10.5, 51.2], "zoom": 4.5, "mod": 1.00, "weight": 8,
     "cities": [
         {"name": "Hamburg", "lon": 10.0, "lat": 53.6, "weight": 3},
         {"name": "Berlin", "lon": 13.4, "lat": 52.5, "weight": 2},
         {"name": "Munich", "lon": 11.6, "lat": 48.1, "weight": 2},
         {"name": "Frankfurt", "lon": 8.7, "lat": 50.1, "weight": 2},
     ]},
    {"name": "Netherlands", "code": "NL", "continent": "Europe",
     "center": [5.3, 52.1], "zoom": 6.5, "mod": 0.90, "weight": 6,
     "cities": [
         {"name": "Rotterdam", "lon": 4.5, "lat": 51.9, "weight": 3},
         {"name": "Amsterdam", "lon": 4.9, "lat": 52.4, "weight": 2},
     ]},
    {"name": "United Kingdom", "code": "GB", "continent": "Europe",
     "center": [-3.4, 55.4], "zoom": 5.0, "mod": 1.10, "weight": 5,
     "cities": [
         {"name": "London", "lon": -0.1, "lat": 51.5, "weight": 3},
         {"name": "Manchester", "lon": -2.2, "lat": 53.5, "weight": 2},
     ]},
    {"name": "France", "code": "FR", "continent": "Europe",
     "center": [2.2, 46.6], "zoom": 5.0, "mod": 1.05, "weight": 4,
     "cities": [
         {"name": "Paris", "lon": 2.3, "lat": 48.9, "weight": 3},
         {"name": "Marseille", "lon": 5.4, "lat": 43.3, "weight": 2},
     ]},
    {"name": "United Arab Emirates", "code": "AE", "continent": "Middle East",
     "center": [54.0, 24.0], "zoom": 6.0, "mod": 1.30, "weight": 5,
     "cities": [
         {"name": "Dubai", "lon": 55.3, "lat": 25.2, "weight": 3},
         {"name": "Abu Dhabi", "lon": 54.4, "lat": 24.5, "weight": 2},
     ]},
    {"name": "Saudi Arabia", "code": "SA", "continent": "Middle East",
     "center": [44.5, 24.0], "zoom": 4.0, "mod": 1.20, "weight": 3,
     "cities": [
         {"name": "Riyadh", "lon": 46.7, "lat": 24.7, "weight": 2},
         {"name": "Jeddah", "lon": 39.2, "lat": 21.5, "weight": 2},
     ]},
    {"name": "Australia", "code": "AU", "continent": "Oceania",
     "center": [133.8, -25.3], "zoom": 3.2, "mod": 1.20, "weight": 5,
     "cities": [
         {"name": "Sydney", "lon": 151.2, "lat": -33.9, "weight": 3},
         {"name": "Melbourne", "lon": 145.0, "lat": -37.8, "weight": 2},
         {"name": "Perth", "lon": 115.9, "lat": -31.9, "weight": 1},
     ]},
]

ORIGINS = [
    ("Shenzhen", "China"), ("Guangzhou", "China"), ("Ningbo", "China"),
    ("Shanghai", "China"), ("Hong Kong", "China"), ("Qingdao", "China"),
    ("Singapore", "Singapore"), ("Tokyo", "Japan"), ("Busan", "South Korea"),
]

DELAY_REASONS = ["Weather", "Customs Clearance", "Capacity Constraint",
                 "Address Issue", "Unknown", "Carrier Delay", "Port Congestion"]

DELAY_DAY_CHOICES = [1, 2, 3, 4, 5, 6, 7, 10, 14, 20, 30]
DELAY_DAY_WEIGHTS = [22, 25, 15, 12, 8, 6, 5, 4, 2, 1, 0.5]


def _country_weights():
    return [c["weight"] for c in COUNTRIES]


def _make_one(rng, ship_id, country_weights):
    ship_date = date.today() - timedelta(days=rng.randint(1, 120))
    sla_days = rng.randint(3, 14)
    expected = ship_date + timedelta(days=sla_days)
    carrier = rng.choice(CARRIERS)
    priority = rng.choices(PRIORITIES, weights=[0.7, 0.25, 0.05], k=1)[0]
    country = rng.choices(COUNTRIES, weights=country_weights, k=1)[0]
    city = rng.choices(country["cities"],
                       weights=[c["weight"] for c in country["cities"]], k=1)[0]
    origin_name, origin_country = rng.choice(ORIGINS)

    p_delay = CARRIER_BASE_DELAY[carrier] * country["mod"]
    roll = rng.random()
    if roll < 0.82:
        status = "Delivered"
    elif roll < 0.94:
        status = "In Transit"
    else:
        status = "Exception"

    actual, delay_reason = None, None
    if status == "Delivered":
        if rng.random() < p_delay:
            delay = rng.choices(DELAY_DAY_CHOICES, weights=DELAY_DAY_WEIGHTS, k=1)[0]
            actual = expected + timedelta(days=delay)
            delay_reason = rng.choice(DELAY_REASONS)
        else:
            actual = expected + timedelta(days=rng.randint(-4, 0))
    elif status == "Exception":
        delay_reason = rng.choice(DELAY_REASONS)

    order_qty = rng.randint(1, 100)
    if status == "Delivered":
        delivered_qty = order_qty if rng.random() > 0.08 else max(1, int(order_qty * rng.uniform(0.6, 0.95)))
    else:
        delivered_qty = 0

    if expected:
        eta_offset = rng.randint(-2, 2)
        estimated_arrival = (expected + timedelta(days=eta_offset)).isoformat()
    else:
        estimated_arrival = None

    line_haul = round(rng.uniform(400, 3500) * (1.5 if priority == "Express" else 1.0), 2)
    fuel = round(line_haul * rng.uniform(0.08, 0.15), 2)
    accessorial = round(rng.uniform(30, 250), 2)
    detention = round(rng.uniform(0, 200) if status != "Delivered" else rng.uniform(0, 60), 2)
    total_cost = round(line_haul + fuel + accessorial + detention, 2)

    return (
        ship_id,
        ship_date.isoformat(),
        expected.isoformat(),
        actual.isoformat() if actual else None,
        estimated_arrival,
        carrier,
        origin_name,
        origin_country,
        city["name"],
        country["name"],
        country["code"],
        country["continent"],
        city["lon"],
        city["lat"],
        status,
        priority,
        sla_days,
        order_qty,
        delivered_qty,
        line_haul,
        fuel,
        accessorial,
        detention,
        total_cost,
        delay_reason,
    )


def generate_shipments_batches(n=50_000, batch_size=5_000, seed=42, start_idx=100000):
    """数据量从 20 万降到 5 万，加快首屏加载和 filter 响应。"""
    rng = random.Random(seed)
    cw = _country_weights()
    batch = []
    for i in range(n):
        batch.append(_make_one(rng, f"SHP-{start_idx + i}", cw))
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def generate_incremental_batch(n=500, seed=None):
    rng = random.Random(seed if seed is not None else random.randint(0, 10**9))
    cw = _country_weights()
    # 用 uuid 前缀，彻底杜绝主键冲突导致的缓存/DB 不一致
    run_id = uuid.uuid4().hex[:8]
    return [_make_one(rng, f"SHP-{run_id}-{i:04d}", cw) for i in range(n)]


CONTINENT_VIEWS = {
    "Asia": {"center": [100, 30], "zoom": 2.4},
    "Europe": {"center": [15, 52], "zoom": 3.8},
    "North America": {"center": [-100, 40], "zoom": 2.4},
    "Middle East": {"center": [48, 28], "zoom": 4.0},
    "Oceania": {"center": [135, -25], "zoom": 3.0},
}