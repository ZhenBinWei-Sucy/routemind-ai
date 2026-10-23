from datetime import date, datetime, timedelta


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def get_delay_days(s):
    exp = parse_date(s.get("expected_delivery_date"))
    act = parse_date(s.get("actual_delivery_date"))
    if not exp or not act:
        return None
    return (act - exp).days


def get_eta_offset(s):
    est = parse_date(s.get("estimated_arrival"))
    act = parse_date(s.get("actual_delivery_date"))
    if not est or not act:
        return None
    return (act - est).days


def is_delivered(s):
    return (s.get("status") == "Delivered"
            and bool(s.get("actual_delivery_date"))
            and bool(s.get("expected_delivery_date")))

def is_delayed(s):
    d = get_delay_days(s)
    return d is not None and d > 0


def is_on_time(s):
    d = get_delay_days(s)
    return d is not None and d <= 0


def is_otif(s):
    if not is_delivered(s):
        return False
    on_time = is_on_time(s)
    in_full = (s.get("delivered_quantity") or 0) >= (s.get("order_quantity") or 0)
    return on_time and in_full


def is_eta_accurate(s, tolerance=1):
    o = get_eta_offset(s)
    return o is not None and abs(o) <= tolerance


def in_transit_overdue_days(s, today=None):
    today = today or date.today()
    if s.get("status") != "In Transit":
        return 0
    exp = parse_date(s.get("expected_delivery_date"))
    if not exp:
        return 0
    return max(0, (today - exp).days)


def is_at_risk(s, today=None):
    """在途且今天已经超过 (expected - 1天) → 明天可能超期"""
    today = today or date.today()
    if s.get("status") != "In Transit":
        return False
    exp = parse_date(s.get("expected_delivery_date"))
    if not exp:
        return False
    return today > (exp - timedelta(days=1))


def percentile(values, p):
    if not values:
        return None
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    return round(vals[f] + (vals[c] - vals[f]) * (k - f), 2)


def apply_filters(shipments, filters):
    result = shipments
    if filters.get("date_range_days"):
        cutoff = date.today() - timedelta(days=int(filters["date_range_days"]))
        result = [s for s in result
                  if parse_date(s["ship_date"]) and parse_date(s["ship_date"]) >= cutoff]
    if filters.get("carrier"):
        result = [s for s in result if s["carrier"] == filters["carrier"]]
    if filters.get("priority"):
        result = [s for s in result if s.get("priority") == filters["priority"]]
    if filters.get("continent"):
        result = [s for s in result if s.get("destination_continent") == filters["continent"]]
    if filters.get("country"):
        result = [s for s in result if s.get("destination_country") == filters["country"]]

    min_d = filters.get("min_delay_days")
    max_d = filters.get("max_delay_days")
    if min_d not in (None, "") or max_d not in (None, ""):
        # 与 get_delay_range_stats 口径对齐：min 为空时取 1，不纳入 d=0
        mn = int(min_d) if min_d not in (None, "") else 1
        mx = int(max_d) if max_d not in (None, "") else 10**6
        out = []
        for s in result:
            d = get_delay_days(s)
            if d is not None and mn <= d <= mx:
                out.append(s)
        result = out
    return result


def _empty_metrics():
    return {
        "total_shipments": 0, "delivered_count": 0, "delayed_count": 0,
        "on_time_count": 0, "otif_count": 0, "eta_accurate_count": 0,
        "in_transit_count": 0, "exception_count": 0, "at_risk_count": 0,
        "delay_rate": None, "on_time_rate": None, "otif_rate": None,
        "eta_accuracy_rate": None, "exception_rate": None,
        "avg_delay_days": None, "p90_delay_days": None,
        "revenue": 0.0, "line_haul_total": 0.0, "fuel_total": 0.0,
        "accessorial_total": 0.0, "detention_total": 0.0,
        "avg_cost_per_shipment": None, "cost_per_delivered": None,
    }


def calculate_metrics(shipments, today=None):
    today = today or date.today()
    m = _empty_metrics()
    m["total_shipments"] = len(shipments)
    if not shipments:
        return m

    delivered, delays, eta_offsets = [], [], []
    for s in shipments:
        m["revenue"] += s.get("shipping_cost") or 0
        m["line_haul_total"] += s.get("line_haul_cost") or 0
        m["fuel_total"] += s.get("fuel_surcharge") or 0
        m["accessorial_total"] += s.get("accessorial_charges") or 0
        m["detention_total"] += s.get("detention_cost") or 0

        st = s.get("status")
        if st == "In Transit":
            m["in_transit_count"] += 1
            if is_at_risk(s, today=today):
                m["at_risk_count"] += 1
        elif st == "Exception":
            m["exception_count"] += 1
        elif st == "Delivered":
            d = get_delay_days(s)
            if d is None:
                continue
            delivered.append(s)
            delays.append(d)
            if d > 0:
                m["delayed_count"] += 1
            else:
                m["on_time_count"] += 1
            if is_otif(s):
                m["otif_count"] += 1
            o = get_eta_offset(s)
            if o is not None:
                eta_offsets.append(o)
                if abs(o) <= 1:
                    m["eta_accurate_count"] += 1

    m["delivered_count"] = len(delivered)
    for k in ("revenue", "line_haul_total", "fuel_total",
              "accessorial_total", "detention_total"):
        m[k] = round(m[k], 2)

    if delivered:
        n = len(delivered)
        m["delay_rate"] = round(m["delayed_count"] / n * 100, 1)
        m["on_time_rate"] = round(m["on_time_count"] / n * 100, 1)
        m["otif_rate"] = round(m["otif_count"] / n * 100, 1)
        m["avg_delay_days"] = round(sum(max(0, d) for d in delays) / n, 2)
        p90 = percentile([max(0, d) for d in delays], 90)
        m["p90_delay_days"] = p90
        if eta_offsets:
            m["eta_accuracy_rate"] = round(
                len([o for o in eta_offsets if abs(o) <= 1]) / len(eta_offsets) * 100, 1)

    if m["total_shipments"]:
        m["exception_rate"] = round(m["exception_count"] / m["total_shipments"] * 100, 1)
        m["avg_cost_per_shipment"] = round(m["revenue"] / m["total_shipments"], 2)
    if m["delivered_count"]:
        m["cost_per_delivered"] = round(m["revenue"] / m["delivered_count"], 2)

    return m


def group_by(shipments, key):
    groups = {}
    for s in shipments:
        groups.setdefault(s.get(key) or "Unknown", []).append(s)
    out = [{"name": k, **calculate_metrics(v)} for k, v in groups.items()]
    return sorted(out, key=lambda x: x["total_shipments"], reverse=True)


def get_country_stats(shipments):
    groups = {}
    for s in shipments:
        n = s.get("destination_country") or "Unknown"
        if n not in groups:
            groups[n] = {
                "code": s.get("destination_country_code") or "",
                "continent": s.get("destination_continent") or "",
                "lon": s.get("destination_lon"),
                "lat": s.get("destination_lat"),
                "items": [],
            }
        groups[n]["items"].append(s)
    out = []
    for n, d in groups.items():
        m = calculate_metrics(d["items"])
        out.append({"name": n, "code": d["code"], "continent": d["continent"],
                    "lon": d["lon"], "lat": d["lat"], **m})
    out.sort(key=lambda x: (x["delay_rate"] if x["delay_rate"] is not None else -1), reverse=True)
    return out


def get_continent_stats(shipments):
    g = {}
    for s in shipments:
        c = s.get("destination_continent") or "Unknown"
        g.setdefault(c, []).append(s)
    out = [{"name": k, **calculate_metrics(v)} for k, v in g.items()]
    out.sort(key=lambda x: (x["delay_rate"] if x["delay_rate"] is not None else -1), reverse=True)
    return out


def get_city_stats(shipments, country=None):
    g = {}
    for s in shipments:
        if country and s.get("destination_country") != country:
            continue
        c = s.get("destination") or "Unknown"
        if c not in g:
            g[c] = {
                "lon": s.get("destination_lon"),
                "lat": s.get("destination_lat"),
                "country": s.get("destination_country"),
                "items": [],
            }
        g[c]["items"].append(s)
    out = []
    for c, d in g.items():
        m = calculate_metrics(d["items"])
        out.append({"name": c, "lon": d["lon"], "lat": d["lat"],
                    "country": d["country"], **m})
    out.sort(key=lambda x: (x["delay_rate"] if x["delay_rate"] is not None else -1), reverse=True)
    return out


def get_lane_stats(shipments, top=15):
    g = {}
    for s in shipments:
        key = f"{s.get('origin_country', '?')} → {s.get('destination_country', '?')}"
        g.setdefault(key, []).append(s)
    out = [{"lane": k, **calculate_metrics(v)} for k, v in g.items() if len(v) >= 10]
    out.sort(key=lambda x: x["total_shipments"], reverse=True)
    return out[:top]


def get_reason_carrier_matrix(shipments):
    carriers, reasons = [], []
    matrix = {}
    for s in shipments:
        if not is_delayed(s):
            continue
        c = s.get("carrier") or "?"
        r = s.get("delay_reason") or "Unknown"
        if c not in carriers:
            carriers.append(c)
        if r not in reasons:
            reasons.append(r)
        matrix.setdefault(c, {}).setdefault(r, 0)
        matrix[c][r] += 1
    return {"carriers": carriers, "reasons": reasons, "matrix": matrix}


def get_cost_breakdown(shipments):
    m = calculate_metrics(shipments)
    return {
        "line_haul": m["line_haul_total"],
        "fuel": m["fuel_total"],
        "accessorial": m["accessorial_total"],
        "detention": m["detention_total"],
        "total": m["revenue"],
    }


def get_status_distribution(shipments):
    d = {"Delivered": 0, "In Transit": 0, "Exception": 0}
    for s in shipments:
        st = s.get("status")
        if st in d:
            d[st] += 1
    return d


def get_delay_reasons(shipments):
    g = {}
    for s in shipments:
        if not is_delayed(s):
            continue
        r = s.get("delay_reason") or "Unknown"
        g[r] = g.get(r, 0) + 1
    return [{"name": k, "count": v} for k, v in
            sorted(g.items(), key=lambda kv: kv[1], reverse=True)]


def get_delay_trend(shipments, days=30):
    today = date.today()
    buckets = {}
    for s in shipments:
        d = parse_date(s["ship_date"])
        if d:
            buckets.setdefault(d, []).append(s)
    trend = []
    for i in range(days, -1, -1):
        d = today - timedelta(days=i)
        items = buckets.get(d, [])
        m = calculate_metrics(items)
        trend.append({
            "date": d.isoformat(),
            "delay_rate": m["delay_rate"] if m["delay_rate"] is not None else 0,
            "delayed_count": m["delayed_count"],
            "total": m["total_shipments"],
        })
    return trend


def get_delay_range_stats(shipments, min_delay, max_delay):
    if min_delay in (None, "") and max_delay in (None, ""):
        return {"active": False}

    mn = int(min_delay) if min_delay not in (None, "") else 1
    mx = int(max_delay) if max_delay not in (None, "") else 10**9
    rd = td = 0
    total = len(shipments)
    for s in shipments:
        d = get_delay_days(s)
        if d is None or d <= 0:
            continue
        td += 1
        if mn <= d <= mx:
            rd += 1
    return {
        "active": True,
        "range_min": mn,
        "range_max": mx if mx < 10**9 else None,
        "range_delayed": rd,
        "total_delayed": td,
        "total_shipments": total,
        "pct_of_delayed": round(rd / td * 100, 1) if td else None,
        "pct_of_total": round(rd / total * 100, 1) if total else None,
    }


def get_at_risk_shipments(shipments, limit=100):
    out = []
    today = date.today()
    for s in shipments:
        if s.get("status") != "In Transit":
            continue
        exp = parse_date(s.get("expected_delivery_date"))
        if not exp:
            continue
        days_left = (exp - today).days
        out.append({**s,
                    "days_left": days_left,
                    "overdue_days": max(0, -days_left),
                    "is_risk": is_at_risk(s, today=today)})
    out.sort(key=lambda x: x["days_left"])
    return out[:limit]


def get_data_quality(shipments):
    total = len(shipments)
    missing_expected = sum(1 for s in shipments if not s.get("expected_delivery_date"))
    missing_actual = sum(1 for s in shipments
                         if s.get("status") == "Delivered" and not s.get("actual_delivery_date"))
    missing_qty = sum(1 for s in shipments if not s.get("order_quantity"))
    return {
        "total": total,
        "missing_expected_date": missing_expected,
        "missing_actual_date": missing_actual,
        "missing_quantity": missing_qty,
        "quality_pct": round((total - missing_expected - missing_actual) / total * 100, 1) if total else None,
    }