from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


SOURCE = Path("/Users/sasad/Downloads/AU.xlsx")
OUTPUT = Path("/Users/sasad/Documents/New project/outputs/au-dashboard/au-dashboard.html")

MONTHS = {
    "Январь": (1, "янв"),
    "Февраль": (2, "фев"),
    "Март": (3, "мар"),
    "Апрель": (4, "апр"),
    "Май": (5, "май"),
    "Июнь": (6, "июн"),
    "Июль": (7, "июл"),
    "Август": (8, "авг"),
    "Сентябрь": (9, "сен"),
    "Октябрь": (10, "окт"),
    "Ноябрь": (11, "ноя"),
    "Декабрь": (12, "дек"),
}


def as_number(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        normalized = value.replace("\xa0", "").replace(" ", "").replace(",", ".")
        if normalized.lower() in {"", "нетданных", "nan"}:
            return None
        try:
            return float(normalized)
        except ValueError:
            return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def clean_data() -> list[dict]:
    raw = pd.read_excel(SOURCE, sheet_name=0)
    raw = raw.rename(
        columns={
            "Unnamed: 0": "year",
            "Unnamed: 1": "month",
            "Посетители\nMAU": "mau",
            "Хиты": "hits",
            "Активность": "activity",
            "Посетители \nDAU": "dau",
            "DAU %": "dauPct",
            "Комментарий": "comment",
            "Кол-во сотрудников": "employees",
            "MAU в %": "mauPct",
        }
    )

    records: list[dict] = []
    for _, row in raw.iterrows():
        month_name = str(row["month"]).strip()
        month_number, month_short = MONTHS[month_name]
        year = int(row["year"])
        record = {
            "year": year,
            "month": month_name,
            "monthNumber": month_number,
            "monthShort": month_short,
            "date": f"{year}-{month_number:02d}-01",
            "label": f"{month_short} {year}",
            "mau": as_number(row["mau"]),
            "hits": as_number(row["hits"]),
            "activity": as_number(row["activity"]),
            "dau": as_number(row["dau"]),
            "dauPct": as_number(row["dauPct"]),
            "employees": as_number(row["employees"]),
            "mauPct": as_number(row["mauPct"]),
            "comment": None
            if pd.isna(row["comment"])
            else str(row["comment"]).strip(),
        }
        records.append(record)
    return sorted(records, key=lambda item: item["date"])


def average(values):
    clean = [v for v in values if v is not None]
    return sum(clean) / len(clean) if clean else None


def yearly_summary(records: list[dict]) -> list[dict]:
    result = []
    for year in sorted({item["year"] for item in records}):
        rows = [item for item in records if item["year"] == year]
        hits_values = [item["hits"] for item in rows if item["hits"] is not None]
        result.append(
            {
                "year": year,
                "months": len(rows),
                "avgMau": average([item["mau"] for item in rows]),
                "avgDau": average([item["dau"] for item in rows]),
                "avgDauPct": average([item["dauPct"] for item in rows]),
                "avgMauPct": average([item["mauPct"] for item in rows]),
                "hitsSum": sum(hits_values) if hits_values else None,
                "hitsMonths": len(hits_values),
            }
        )
    return result


DATA = clean_data()
YEARLY = yearly_summary(DATA)
YEARS = sorted({item["year"] for item in DATA})
START_LABEL = DATA[0]["label"]
END_LABEL = DATA[-1]["label"]
LATEST_HITS = next(item for item in reversed(DATA) if item["hits"] is not None)

html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AU dashboard</title>
  <style>
    :root {{
      --bg: #f7f7f4;
      --panel: #ffffff;
      --panel-2: #f1f3f2;
      --ink: #111418;
      --muted: #5e6673;
      --line: #d6dadf;
      --blue: #005bbb;
      --orange: #ff6b35;
      --green: #12805c;
      --yellow: #f2b705;
      --red: #c84335;
      --shadow: 0 16px 34px rgba(17, 20, 24, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    button, select {{ font: inherit; }}
    .shell {{
      width: min(1420px, calc(100% - 48px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}
    .topbar {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 24px;
      align-items: start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 22px;
    }}
    .eyebrow {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: 38px;
      line-height: 1.04;
      max-width: 780px;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      white-space: normal;
    }}
    .controls {{
      display: grid;
      gap: 12px;
      justify-items: end;
    }}
    .select-wrap {{
      display: grid;
      gap: 6px;
      min-width: 210px;
    }}
    .select-wrap label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      padding: 11px 12px;
      min-height: 44px;
    }}
    .segment {{
      display: grid;
      grid-template-columns: repeat(3, minmax(90px, 1fr));
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      background: var(--panel);
      min-height: 44px;
    }}
    .segment button {{
      border: 0;
      border-right: 1px solid var(--line);
      background: transparent;
      color: var(--muted);
      padding: 10px 12px;
      font-size: 14px;
      font-weight: 800;
      cursor: pointer;
    }}
    .segment button:last-child {{ border-right: 0; }}
    .segment button.active {{
      background: var(--ink);
      color: #ffffff;
    }}
    .status {{
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
      max-width: 900px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
      margin: 22px 0;
    }}
    .kpi {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 146px;
      display: grid;
      align-content: space-between;
      box-shadow: var(--shadow);
    }}
    .kpi .label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
      line-height: 1.25;
    }}
    .kpi .value {{
      margin: 12px 0 8px;
      font-size: 30px;
      line-height: 1;
      font-weight: 900;
      overflow-wrap: anywhere;
    }}
    .kpi .note {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }}
    .delta {{
      display: inline-flex;
      width: fit-content;
      max-width: 100%;
      border-radius: 6px;
      padding: 4px 7px;
      font-size: 12px;
      font-weight: 850;
      line-height: 1.15;
      white-space: normal;
    }}
    .delta.up {{ background: rgba(18, 128, 92, 0.12); color: var(--green); }}
    .delta.down {{ background: rgba(200, 67, 53, 0.12); color: var(--red); }}
    .delta.neutral {{ background: var(--panel-2); color: var(--muted); }}
    .grid-2 {{
      display: grid;
      grid-template-columns: minmax(0, 1.9fr) minmax(320px, 0.9fr);
      gap: 16px;
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .panel-head {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 18px 0;
    }}
    .panel h2 {{
      margin: 0;
      font-size: 20px;
      line-height: 1.18;
    }}
    .panel .sub {{
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }}
    .chart-wrap {{
      padding: 8px 12px 16px;
      min-height: 420px;
    }}
    svg {{
      display: block;
      width: 100%;
      height: auto;
      overflow: visible;
    }}
    .axis text {{
      fill: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }}
    .gridline {{
      stroke: #e7e9ec;
      stroke-width: 1;
      shape-rendering: crispEdges;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0 18px 14px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 750;
    }}
    .legend span {{
      display: inline-flex;
      gap: 7px;
      align-items: center;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 3px;
      background: var(--blue);
      flex: 0 0 auto;
    }}
    .dot.orange {{ background: var(--orange); }}
    .dot.green {{ background: var(--green); }}
    .dot.yellow {{ background: var(--yellow); }}
    .side-stack {{
      display: grid;
      gap: 16px;
    }}
    .info-list {{
      display: grid;
      gap: 12px;
      padding: 16px 18px 18px;
    }}
    .info-row {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}
    .info-row:first-child {{
      border-top: 0;
      padding-top: 0;
    }}
    .info-row b {{
      display: block;
      font-size: 15px;
      line-height: 1.25;
      margin-bottom: 4px;
    }}
    .info-row span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.42;
    }}
    .grid-bottom {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
      margin-top: 16px;
    }}
    .coverage-chart {{
      padding: 8px 12px 16px;
      min-height: 280px;
    }}
    .table-panel {{
      margin-top: 16px;
      overflow: hidden;
    }}
    .table-scroll {{
      overflow-x: auto;
      padding: 8px 18px 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 880px;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: right;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 850;
      background: #fafafa;
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    th:first-child, td:first-child {{
      text-align: left;
      font-weight: 800;
    }}
    td.comment {{
      text-align: left;
      max-width: 280px;
      overflow-wrap: anywhere;
      color: var(--muted);
    }}
    .footnote {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }}
    @media (max-width: 1120px) {{
      .shell {{ width: min(100% - 32px, 980px); }}
      .topbar, .grid-2, .grid-bottom {{
        grid-template-columns: 1fr;
      }}
      .controls {{ justify-items: stretch; }}
      .kpi-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .kpi:last-child {{ grid-column: 1 / -1; }}
    }}
    @media (max-width: 640px) {{
      .shell {{
        width: calc(100% - 24px);
        padding-top: 18px;
      }}
      h1 {{ font-size: 29px; }}
      .kpi-grid {{ grid-template-columns: 1fr; }}
      .kpi:last-child {{ grid-column: auto; }}
      .segment {{
        grid-template-columns: 1fr;
      }}
      .segment button {{
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      .segment button:last-child {{ border-bottom: 0; }}
      .panel-head {{
        display: grid;
      }}
      .chart-wrap {{ min-height: 330px; }}
      .kpi .value {{ font-size: 28px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">AU dashboard</p>
        <h1>Активность пользователей AU</h1>
        <div class="meta">
          <span class="pill">Источник: AU.xlsx · Лист1</span>
          <span class="pill">Период: {START_LABEL} - {END_LABEL}</span>
          <span class="pill">Хиты обновлены до {LATEST_HITS["label"]}</span>
        </div>
        <p class="status" id="statusLine"></p>
      </div>
      <div class="controls" aria-label="Фильтры дашборда">
        <div class="select-wrap">
          <label for="yearFilter">Период</label>
          <select id="yearFilter"></select>
        </div>
        <div class="segment" role="tablist" aria-label="Режим графика">
          <button type="button" class="active" data-mode="users">Пользователи</button>
          <button type="button" data-mode="coverage">Охват</button>
          <button type="button" data-mode="hits">Хиты</button>
        </div>
      </div>
    </header>

    <section class="kpi-grid" id="kpiGrid" aria-label="Ключевые показатели"></section>

    <section class="grid-2">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 id="mainChartTitle">Динамика</h2>
            <p class="sub" id="mainChartSub"></p>
          </div>
        </div>
        <div class="chart-wrap">
          <svg id="mainChart" viewBox="0 0 920 390" role="img" aria-label="Главный график"></svg>
        </div>
        <div class="legend" id="mainLegend"></div>
      </article>

      <aside class="side-stack">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Выводы</h2>
              <p class="sub">Автоматически собраны из последнего доступного периода.</p>
            </div>
          </div>
          <div class="info-list" id="insights"></div>
        </article>
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Качество данных</h2>
              <p class="sub">Где нужно быть осторожнее с интерпретацией.</p>
            </div>
          </div>
          <div class="info-list" id="quality"></div>
        </article>
      </aside>
    </section>

    <section class="grid-bottom">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>Охват по годам</h2>
            <p class="sub">Средний MAU и DAU в процентах от численности сотрудников.</p>
          </div>
        </div>
        <div class="coverage-chart">
          <svg id="coverageChart" viewBox="0 0 700 260" role="img" aria-label="Охват по годам"></svg>
        </div>
        <div class="legend">
          <span><i class="dot green"></i>MAU / сотрудники</span>
          <span><i class="dot orange"></i>DAU / сотрудники</span>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>Что делать дальше</h2>
            <p class="sub">Минимальный набор шагов для управленческого контура.</p>
          </div>
        </div>
        <div class="info-list" id="actions"></div>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-head">
        <div>
          <h2>Месячная детализация</h2>
          <p class="sub" id="tableSub"></p>
        </div>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Месяц</th>
              <th>MAU</th>
              <th>DAU</th>
              <th>DAU %</th>
              <th>Сотрудники</th>
              <th>MAU %</th>
              <th>Хиты</th>
              <th>Активность</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody id="dataTable"></tbody>
        </table>
      </div>
    </section>

    <p class="footnote">Карта не строится: в исходном файле нет географических измерений. Пропуски в источнике показаны как "н/д" и не подменяются нулями.</p>
  </main>

  <script>
    const DATA = {json.dumps(DATA, ensure_ascii=False, allow_nan=False)};
    const YEARLY = {json.dumps(YEARLY, ensure_ascii=False, allow_nan=False)};
    const YEARS = {json.dumps(YEARS, ensure_ascii=False)};
    const state = {{ year: "all", mode: "users" }};

    const colors = {{
      blue: "#005bbb",
      orange: "#ff6b35",
      green: "#12805c",
      yellow: "#f2b705",
      muted: "#5e6673",
      line: "#d6dadf",
      grid: "#e7e9ec",
      ink: "#111418"
    }};

    function cleanNumber(value) {{
      return typeof value === "number" && Number.isFinite(value) ? value : null;
    }}

    function fmtNum(value, digits = 0) {{
      const n = cleanNumber(value);
      if (n === null) return "н/д";
      return new Intl.NumberFormat("ru-RU", {{ maximumFractionDigits: digits, minimumFractionDigits: digits }}).format(n);
    }}

    function fmtPct(value, digits = 1) {{
      const n = cleanNumber(value);
      if (n === null) return "н/д";
      return `${{fmtNum(n, digits)}}%`;
    }}

    function rowsForState() {{
      if (state.year === "all") return DATA;
      return DATA.filter(row => String(row.year) === state.year);
    }}

    function latestWith(rows, key) {{
      return [...rows].reverse().find(row => cleanNumber(row[key]) !== null) || null;
    }}

    function byDate(date) {{
      return DATA.find(row => row.date === date) || null;
    }}

    function shiftedDate(date, months) {{
      const parsed = new Date(`${{date}}T00:00:00`);
      parsed.setMonth(parsed.getMonth() + months);
      return `${{parsed.getFullYear()}}-${{String(parsed.getMonth() + 1).padStart(2, "0")}}-01`;
    }}

    function deltaFor(row, key, months) {{
      if (!row) return null;
      const current = cleanNumber(row[key]);
      const previousRow = byDate(shiftedDate(row.date, months));
      const previous = previousRow ? cleanNumber(previousRow[key]) : null;
      if (current === null || previous === null || previous === 0) return null;
      return (current - previous) / Math.abs(previous);
    }}

    function pointDeltaFor(row, key, months) {{
      if (!row) return null;
      const current = cleanNumber(row[key]);
      const previousRow = byDate(shiftedDate(row.date, months));
      const previous = previousRow ? cleanNumber(previousRow[key]) : null;
      if (current === null || previous === null) return null;
      return current - previous;
    }}

    function deltaBadge(value, suffix = "%", pointMode = false) {{
      const n = cleanNumber(value);
      if (n === null) return `<span class="delta neutral">нет базы</span>`;
      const cls = n > 0 ? "up" : n < 0 ? "down" : "neutral";
      const sign = n > 0 ? "+" : "";
      const shown = pointMode ? fmtNum(n, 1) : fmtNum(n * 100, 1);
      return `<span class="delta ${{cls}}">${{sign}}${{shown}}${{suffix}} г/г</span>`;
    }}

    function valueLabel(row, key) {{
      const value = cleanNumber(row?.[key]);
      return value === null ? "нет данных" : row.label;
    }}

    function renderControls() {{
      const select = document.querySelector("#yearFilter");
      select.innerHTML = `<option value="all">Все годы</option>` + YEARS.map(year => `<option value="${{year}}">${{year}}</option>`).join("");
      select.value = state.year;
      select.addEventListener("change", event => {{
        state.year = event.target.value;
        renderAll();
      }});
      document.querySelectorAll("[data-mode]").forEach(button => {{
        button.addEventListener("click", () => {{
          state.mode = button.dataset.mode;
          document.querySelectorAll("[data-mode]").forEach(item => item.classList.toggle("active", item.dataset.mode === state.mode));
          renderAll();
        }});
      }});
    }}

    function renderStatus(rows) {{
      const start = rows[0]?.label || "";
      const end = rows[rows.length - 1]?.label || "";
      const hitsLatest = latestWith(rows, "hits");
      const dauLatest = latestWith(rows, "dau");
      const text = state.year === "all"
        ? `Показываю весь ряд: ${{start}} - ${{end}}. DAU есть с ${{DATA.find(row => cleanNumber(row.dau) !== null)?.label}}, хиты и активность заполнены до ${{latestWith(DATA, "hits")?.label}}.`
        : `Показываю ${{state.year}} год: ${{rows.length}} месяцев. Последний DAU: ${{valueLabel(dauLatest, "dau")}}, последние хиты: ${{valueLabel(hitsLatest, "hits")}}.`;
      document.querySelector("#statusLine").textContent = text;
    }}

    function renderKpis(rows) {{
      const mauRow = latestWith(rows, "mau");
      const dauRow = latestWith(rows, "dau");
      const dauPctRow = latestWith(rows, "dauPct");
      const mauPctRow = latestWith(rows, "mauPct");
      const hitsRow = latestWith(rows, "hits");
      const items = [
        {{
          label: "MAU",
          value: fmtNum(mauRow?.mau),
          note: `${{valueLabel(mauRow, "mau")}} · активная месячная аудитория`,
          badge: deltaBadge(deltaFor(mauRow, "mau", -12))
        }},
        {{
          label: "DAU",
          value: fmtNum(dauRow?.dau),
          note: `${{valueLabel(dauRow, "dau")}} · ежедневная аудитория`,
          badge: deltaBadge(deltaFor(dauRow, "dau", -12))
        }},
        {{
          label: "DAU / сотрудники",
          value: fmtPct(dauPctRow?.dauPct),
          note: `${{valueLabel(dauPctRow, "dauPct")}} · глубина ежедневного использования`,
          badge: deltaBadge(pointDeltaFor(dauPctRow, "dauPct", -12), " п.п. г/г", true)
        }},
        {{
          label: "MAU / сотрудники",
          value: fmtPct(mauPctRow?.mauPct),
          note: `${{valueLabel(mauPctRow, "mauPct")}} · почти полный месячный охват`,
          badge: deltaBadge(pointDeltaFor(mauPctRow, "mauPct", -12), " п.п. г/г", true)
        }},
        {{
          label: "Хиты",
          value: fmtNum(hitsRow?.hits),
          note: `${{valueLabel(hitsRow, "hits")}} · активность: ${{fmtNum(hitsRow?.activity, 1)}}`,
          badge: deltaBadge(deltaFor(hitsRow, "hits", -12))
        }}
      ];
      document.querySelector("#kpiGrid").innerHTML = items.map(item => `
        <article class="kpi">
          <div>
            <div class="label">${{item.label}}</div>
            <div class="value">${{item.value}}</div>
            ${{item.badge}}
          </div>
          <div class="note">${{item.note}}</div>
        </article>
      `).join("");
    }}

    function scaleLinear(domainMin, domainMax, rangeMin, rangeMax) {{
      const span = domainMax - domainMin || 1;
      return value => rangeMax - ((value - domainMin) / span) * (rangeMax - rangeMin);
    }}

    function niceMax(values, fallback = 10) {{
      const max = Math.max(...values.filter(value => cleanNumber(value) !== null), fallback);
      const pow = Math.pow(10, Math.floor(Math.log10(max)));
      return Math.ceil(max / pow) * pow;
    }}

    function labelTicks(max, pct = false) {{
      return [0, max * 0.25, max * 0.5, max * 0.75, max].map(value => pct ? fmtPct(value, 0) : fmtNum(value));
    }}

    function linePath(rows, key, xScale, yScale) {{
      let path = "";
      rows.forEach((row, index) => {{
        const value = cleanNumber(row[key]);
        if (value === null) return;
        const x = xScale(index);
        const y = yScale(value);
        path += `${{path ? "L" : "M"}}${{x.toFixed(2)}},${{y.toFixed(2)}}`;
      }});
      return path;
    }}

    function renderMainChart(rows) {{
      const svg = document.querySelector("#mainChart");
      const legend = document.querySelector("#mainLegend");
      const title = document.querySelector("#mainChartTitle");
      const sub = document.querySelector("#mainChartSub");
      const width = 920;
      const height = 390;
      const pad = {{ left: 64, right: 28, top: 26, bottom: 52 }};
      const plotW = width - pad.left - pad.right;
      const plotH = height - pad.top - pad.bottom;
      const xScale = index => pad.left + (rows.length <= 1 ? 0 : (index / (rows.length - 1)) * plotW);

      let body = "";
      const xTicks = rows.map((row, index) => ({{ row, index }})).filter((_, index) => {{
        const step = rows.length > 36 ? 12 : rows.length > 16 ? 4 : 2;
        return index % step === 0 || index === rows.length - 1;
      }});

      if (state.mode === "hits") {{
        title.textContent = "Хиты";
        sub.textContent = "После февраля 2025 в источнике нет значений, поэтому хвост ряда оставлен пустым.";
        const max = niceMax(rows.map(row => row.hits), 1000000);
        const yScale = scaleLinear(0, max, pad.top, pad.top + plotH);
        [0, 0.25, 0.5, 0.75, 1].forEach(tick => {{
          const y = pad.top + plotH * tick;
          body += `<line class="gridline" x1="${{pad.left}}" y1="${{y}}" x2="${{width - pad.right}}" y2="${{y}}"></line>`;
        }});
        labelTicks(max).forEach((label, index) => {{
          const y = pad.top + plotH - (plotH * index / 4);
          body += `<text x="${{pad.left - 10}}" y="${{y + 4}}" text-anchor="end" class="axis">${{label}}</text>`;
        }});
        const barWidth = Math.max(4, Math.min(16, plotW / Math.max(rows.length, 1) * 0.58));
        rows.forEach((row, index) => {{
          const value = cleanNumber(row.hits);
          if (value === null) return;
          const x = xScale(index) - barWidth / 2;
          const y = yScale(value);
          body += `<rect x="${{x.toFixed(2)}}" y="${{y.toFixed(2)}}" width="${{barWidth.toFixed(2)}}" height="${{(pad.top + plotH - y).toFixed(2)}}" fill="${{colors.blue}}" opacity="0.82"></rect>`;
        }});
        legend.innerHTML = `<span><i class="dot"></i>Хиты</span><span><i class="dot yellow"></i>Активность показана в KPI и таблице</span>`;
      }} else {{
        const isCoverage = state.mode === "coverage";
        title.textContent = isCoverage ? "Охват аудитории" : "Пользователи";
        sub.textContent = isCoverage ? "Процент сотрудников, которые используют AU в месяц и в день." : "MAU доступен за весь период, DAU начинается с марта 2022.";
        const series = isCoverage
          ? [
              {{ key: "mauPct", label: "MAU / сотрудники", color: colors.green }},
              {{ key: "dauPct", label: "DAU / сотрудники", color: colors.orange }}
            ]
          : [
              {{ key: "mau", label: "MAU", color: colors.blue }},
              {{ key: "dau", label: "DAU", color: colors.orange }}
            ];
        const values = series.flatMap(item => rows.map(row => row[item.key])).filter(value => cleanNumber(value) !== null);
        const max = isCoverage ? Math.max(100, niceMax(values, 100)) : niceMax(values, 10000);
        const yScale = scaleLinear(0, max, pad.top, pad.top + plotH);
        [0, 0.25, 0.5, 0.75, 1].forEach(tick => {{
          const y = pad.top + plotH * tick;
          body += `<line class="gridline" x1="${{pad.left}}" y1="${{y}}" x2="${{width - pad.right}}" y2="${{y}}"></line>`;
        }});
        labelTicks(max, isCoverage).forEach((label, index) => {{
          const y = pad.top + plotH - (plotH * index / 4);
          body += `<text x="${{pad.left - 10}}" y="${{y + 4}}" text-anchor="end" class="axis">${{label}}</text>`;
        }});
        series.forEach(item => {{
          const d = linePath(rows, item.key, xScale, yScale);
          if (d) body += `<path d="${{d}}" fill="none" stroke="${{item.color}}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"></path>`;
          rows.forEach((row, index) => {{
            const value = cleanNumber(row[item.key]);
            if (value === null) return;
            const x = xScale(index);
            const y = yScale(value);
            body += `<circle cx="${{x.toFixed(2)}}" cy="${{y.toFixed(2)}}" r="3.4" fill="${{item.color}}"></circle>`;
          }});
        }});
        legend.innerHTML = series.map((item, index) => `<span><i class="dot ${{index === 1 ? "orange" : isCoverage ? "green" : ""}}"></i>${{item.label}}</span>`).join("");
      }}

      xTicks.forEach(({{ row, index }}) => {{
        const x = xScale(index);
        body += `<text x="${{x}}" y="${{height - 18}}" text-anchor="middle" class="axis">${{row.monthShort}} ${{String(row.year).slice(2)}}</text>`;
      }});
      body += `<line x1="${{pad.left}}" y1="${{pad.top + plotH}}" x2="${{width - pad.right}}" y2="${{pad.top + plotH}}" stroke="${{colors.line}}"></line>`;
      svg.innerHTML = body;
    }}

    function renderCoverageChart() {{
      const svg = document.querySelector("#coverageChart");
      const rows = YEARLY;
      const width = 700;
      const height = 260;
      const pad = {{ left: 48, right: 24, top: 18, bottom: 42 }};
      const plotW = width - pad.left - pad.right;
      const plotH = height - pad.top - pad.bottom;
      const max = 100;
      const yScale = scaleLinear(0, max, pad.top, pad.top + plotH);
      const group = plotW / rows.length;
      const barW = Math.max(14, group * 0.26);
      let body = "";
      [0, 25, 50, 75, 100].forEach(value => {{
        const y = yScale(value);
        body += `<line class="gridline" x1="${{pad.left}}" y1="${{y}}" x2="${{width - pad.right}}" y2="${{y}}"></line>`;
        body += `<text x="${{pad.left - 9}}" y="${{y + 4}}" text-anchor="end" class="axis">${{value}}%</text>`;
      }});
      rows.forEach((row, index) => {{
        const center = pad.left + group * index + group / 2;
        const values = [
          {{ key: "avgMauPct", color: colors.green, offset: -barW * 0.6 }},
          {{ key: "avgDauPct", color: colors.orange, offset: barW * 0.6 }}
        ];
        values.forEach(item => {{
          const value = cleanNumber(row[item.key]);
          if (value === null) return;
          const y = yScale(value);
          body += `<rect x="${{(center + item.offset - barW / 2).toFixed(2)}}" y="${{y.toFixed(2)}}" width="${{barW.toFixed(2)}}" height="${{(pad.top + plotH - y).toFixed(2)}}" fill="${{item.color}}" rx="2"></rect>`;
        }});
        body += `<text x="${{center}}" y="${{height - 17}}" text-anchor="middle" class="axis">${{row.year}}</text>`;
      }});
      body += `<line x1="${{pad.left}}" y1="${{pad.top + plotH}}" x2="${{width - pad.right}}" y2="${{pad.top + plotH}}" stroke="${{colors.line}}"></line>`;
      svg.innerHTML = body;
    }}

    function renderInsights(rows) {{
      const latestMau = latestWith(rows, "mau");
      const latestDau = latestWith(rows, "dau");
      const latestDauPct = latestWith(rows, "dauPct");
      const latestMauPct = latestWith(rows, "mauPct");
      const latestHits = latestWith(rows, "hits");
      const items = [
        [
          "Месячный охват близок к потолку",
          `${{latestMauPct?.label || "Последний период"}}: ${{fmtPct(latestMauPct?.mauPct)}} сотрудников заходили в AU за месяц. Это зона удержания, а не первичного внедрения.`
        ],
        [
          "Ежедневное использование растет быстрее",
          `${{latestDau?.label || "Последний период"}}: DAU ${{fmtNum(latestDau?.dau)}}; год к году ${{deltaBadge(deltaFor(latestDau, "dau", -12)).replace(/<[^>]*>/g, "")}}.`
        ],
        [
          "Главная аналитическая дырка - хиты",
          `Хиты и активность в источнике заканчиваются на ${{latestHits?.label || "н/д"}}. Для свежего операционного дашборда этот ряд нужно обновить.`
        ],
        [
          "DAU уже стал управленческой метрикой",
          `Последняя доля DAU: ${{fmtPct(latestDauPct?.dauPct)}}. Ее удобно использовать как индикатор регулярности, а MAU - как индикатор охвата.`
        ]
      ];
      document.querySelector("#insights").innerHTML = items.map(([title, text]) => `<div class="info-row"><b>${{title}}</b><span>${{text}}</span></div>`).join("");
    }}

    function renderQuality(rows) {{
      const allHits = DATA.filter(row => cleanNumber(row.hits) !== null);
      const allDau = DATA.filter(row => cleanNumber(row.dau) !== null);
      const allEmployees = DATA.filter(row => cleanNumber(row.employees) !== null);
      const comments = DATA.filter(row => row.comment);
      const items = [
        ["DAU", `Заполнен с ${{allDau[0]?.label}} по ${{allDau[allDau.length - 1]?.label}}; ранние годы сравнивать по DAU нельзя.`],
        ["Хиты и активность", `Заполнены за ${{allHits.length}} месяцев из ${{DATA.length}}; последний месяц: ${{allHits[allHits.length - 1]?.label}}.`],
        ["Сотрудники", `Численность есть за ${{allEmployees.length}} месяцев; проценты MAU/DAU строятся только там, где она заполнена.`],
        ["Комментарии", `${{comments.length}} отмеченное событие: ${{comments[0]?.label || "н/д"}}. Для объяснения пиков стоит вести комментарии регулярно.`]
      ];
      document.querySelector("#quality").innerHTML = items.map(([title, text]) => `<div class="info-row"><b>${{title}}</b><span>${{text}}</span></div>`).join("");
    }}

    function renderActions(rows) {{
      const items = [
        ["Обновить хиты после февраля 2025", "Иначе верхний график пользователей актуален, а блок активности остается историческим."],
        ["Задать целевой коридор DAU", "Для зрелого продукта логичнее управлять не MAU, а ежедневной регулярностью и удержанием."],
        ["Добавлять причины всплесков", "Сейчас в данных почти нет комментариев, поэтому пики сложно объяснять в презентации или штабе."],
        ["Разнести аудитории, если появятся сегменты", "Следующий полезный слой: подразделения, роли или регионы. Тогда можно строить карту или матрицу вовлеченности."]
      ];
      document.querySelector("#actions").innerHTML = items.map(([title, text]) => `<div class="info-row"><b>${{title}}</b><span>${{text}}</span></div>`).join("");
    }}

    function renderTable(rows) {{
      const visible = [...rows].reverse();
      document.querySelector("#tableSub").textContent = `${{visible.length}} строк в выбранном периоде`;
      document.querySelector("#dataTable").innerHTML = visible.map(row => `
        <tr>
          <td>${{row.label}}</td>
          <td>${{fmtNum(row.mau)}}</td>
          <td>${{fmtNum(row.dau)}}</td>
          <td>${{fmtPct(row.dauPct)}}</td>
          <td>${{fmtNum(row.employees)}}</td>
          <td>${{fmtPct(row.mauPct)}}</td>
          <td>${{fmtNum(row.hits)}}</td>
          <td>${{fmtNum(row.activity, 1)}}</td>
          <td class="comment">${{row.comment || "н/д"}}</td>
        </tr>
      `).join("");
    }}

    function renderAll() {{
      const rows = rowsForState();
      renderStatus(rows);
      renderKpis(rows);
      renderMainChart(rows);
      renderCoverageChart();
      renderInsights(rows);
      renderQuality(rows);
      renderActions(rows);
      renderTable(rows);
    }}

    renderControls();
    renderAll();
  </script>
</body>
</html>
"""

OUTPUT.write_text(html, encoding="utf-8")
print(OUTPUT)
