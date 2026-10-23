import re

SUPPORTED_HINT = (
    "Supported: delay diagnosis, carrier performance, country risk, lane analysis, in-transit risk. "
    "Mention 'last N days', 'carrier', 'country', 'lane', 'delay between X-Y days' to refine."
)


def parse_request(text: str) -> dict:
    text = text or ""
    t = text.lower()
    config = {
        "title": "Shipment Delay Analysis",
        "date_range_days": 30,
        "metrics": ["shipment_count", "delay_rate", "on_time_rate", "otif_rate",
                    "eta_accuracy_rate", "exception_rate", "p90_delay_days", "revenue"],
        "group_by": ["carrier", "country"],
        "min_delay_days": None,
        "max_delay_days": None,
    }
    for num in (7, 14, 30, 60, 90):
        if re.search(rf"\b{num}\b", t) or f"{num}天" in text:
            config["date_range_days"] = num
            break
    if "承运商" in text or "carrier" in t:
        if "carrier" not in config["group_by"]:
            config["group_by"].append("carrier")
    if "国家" in text or "country" in t:
        if "country" not in config["group_by"]:
            config["group_by"].append("country")
    if "洲" in text or "continent" in t:
        if "continent" not in config["group_by"]:
            config["group_by"].append("continent")
    if "线路" in text or "lane" in t or "走廊" in text:
        config["group_by"].append("lane")

    m = re.search(r"(超过|大于|>=?|over|above)\s*(\d+)\s*天?", text, re.IGNORECASE)
    if m:
        config["min_delay_days"] = int(m.group(2))

    if "在途" in text or "in transit" in t or "超期" in text:
        config["title"] = "In-Transit Risk Analysis"
    elif ("国家" in text or "country" in t) and "承运商" not in text:
        config["title"] = "Country Risk Analysis"
    elif "承运商" in text and "国家" not in text and "country" not in t:
        config["title"] = "Carrier Performance Analysis"
    elif "线路" in text or "lane" in t:
        config["title"] = "Lane Performance Analysis"
    return config


def parse_followup(text: str, current_filters: dict) -> dict:
    text = text or ""
    t = text.lower()
    updates = {}
    for num in (7, 14, 30, 60, 90):
        if re.search(rf"\b{num}\b", t) or f"{num}天" in text:
            updates["date_range_days"] = num
            break
    m = re.search(r"(超过|大于|>=?|over|above)\s*(\d+)\s*天?", text, re.IGNORECASE)
    if m:
        updates["min_delay_days"] = int(m.group(2))
    if "所有承运商" in text or "all carriers" in t:
        updates["carrier"] = ""
    if "所有国家" in text or "all countries" in t:
        updates["country"] = ""
    if "所有洲" in text or "all continents" in t:
        updates["continent"] = ""
    return updates