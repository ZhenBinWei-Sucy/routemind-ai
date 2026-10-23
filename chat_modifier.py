import re


def apply_chat_modification(text: str, current_config: dict, current_filters: dict):
    """
    返回 (new_config, new_filters, message)
    只处理 MVP 支持的有限修改意图，透明可解释。
    """
    t = (text or "").lower()
    config = dict(current_config or {})
    filters = dict(current_filters or {})
    changed = []

    # 时间范围（用词边界匹配，避免 "1600" 命中 "60"）
    m = re.search(r"\b(\d+)\s*天", text) or re.search(r"\blast\s+(\d+)\s*days?\b", t)
    if m:
        n = int(m.group(1))
        if n in (7, 14, 30, 60, 90):
            filters["date_range_days"] = n
            changed.append(f"时间范围改为最近 {n} 天")

    # 承运商
    carrier_match = re.search(r"(?:只看|筛选|过滤)\s*([A-Za-z][A-Za-z\s]+?)(?:承运商|$)", text)
    if carrier_match:
        filters["carrier"] = carrier_match.group(1).strip()
        changed.append(f"承运商筛选为 {filters['carrier']}")
    if "所有承运商" in text or "全部承运商" in text:
        filters["carrier"] = ""
        changed.append("承运商筛选已清除")

    # 延误阈值
    m = re.search(r"(?:超过|大于|≥|>=)\s*(\d+)\s*天", text)
    if m:
        filters["min_delay_days"] = int(m.group(1))
        changed.append(f"延误阈值改为 ≥ {m.group(1)} 天")

    # 图表类型切换
    if "柱状图" in text and "delay_trend" in config.get("visualizations", []):
        config.setdefault("chart_overrides", {})["delay_trend"] = "bar"
        changed.append("趋势图切换为柱状图")
    if "折线" in text:
        config.setdefault("chart_overrides", {})["delay_trend"] = "line"
        changed.append("趋势图切换为折线图")

    if not changed:
        return config, filters, "当前 MVP 支持的修改包括：时间范围、承运商、延误阈值、趋势图类型。请尝试更具体的描述。"

    return config, filters, "已应用：" + "；".join(changed)