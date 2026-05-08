/* ── Presets ─────────────────────────────────────────────────────────────── */
const PRESETS = {
  high: {
    total_items: 8, total_price: 420, total_freight: 65,
    unique_sellers: 3, payment_installments: 12,
    approval_delay_hours: 72, estimated_delivery_days: 45,
    purchase_month: 11, purchase_weekday: 4,
    seller_historic_risk_rate: 0.38, seller_historic_order_count: 8,
    category_risk_rate: 0.28, is_high_risk_category: 1,
    same_state: 0, customer_is_sp: 0,
  },
  low: {
    total_items: 1, total_price: 95, total_freight: 12,
    unique_sellers: 1, payment_installments: 1,
    approval_delay_hours: 0.5, estimated_delivery_days: 7,
    purchase_month: 4, purchase_weekday: 1,
    seller_historic_risk_rate: 0.05, seller_historic_order_count: 120,
    category_risk_rate: 0.07, is_high_risk_category: 0,
    same_state: 1, customer_is_sp: 1,
  },
};

function loadPreset(type) {
  const p = PRESETS[type];
  Object.entries(p).forEach(([k, v]) => {
    const el = document.getElementById(k);
    if (el) el.value = v;
  });
}

function resetForm() {
  document.getElementById('predictForm').reset();
  hideResult();
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

function hideResult() {
  document.getElementById('resultContent').style.display = 'none';
  document.getElementById('resultPlaceholder').style.display = 'flex';
  document.getElementById('errorBox').style.display = 'none';
}

function showLoading(on) {
  document.getElementById('loadingOverlay').style.display = on ? 'flex' : 'none';
  document.getElementById('submitBtn').disabled = on;
}

/* ── Form submit ─────────────────────────────────────────────────────────── */
document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  showLoading(true);
  document.getElementById('errorBox').style.display = 'none';

  const fd = new FormData(e.target);
  const payload = {};
  for (const [k, v] of fd.entries()) {
    if (k === 'csrfmiddlewaretoken') continue;
    payload[k] = parseFloat(v);
  }

  try {
    const res = await fetch('/api/predict/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    showLoading(false);
    renderResult(data);

  } catch (err) {
    showLoading(false);
    document.getElementById('errorBox').style.display = 'block';
    document.getElementById('errorMsg').textContent = err.message || 'Error de conexión';
  }
});

/* ── Render result ───────────────────────────────────────────────────────── */
function renderResult(data) {
  document.getElementById('resultPlaceholder').style.display = 'none';
  document.getElementById('resultContent').style.display = 'block';

  const isHigh = data.risk_label === 1;
  const prob   = data.risk_probability;
  const thresh = data.threshold;

  // Verdict card
  const card = document.getElementById('verdictCard');
  card.className = 'verdict-card ' + (isHigh ? 'high' : 'low');
  document.getElementById('verdictIcon').textContent = isHigh ? '🔴' : '🟢';
  document.getElementById('verdictText').textContent = data.risk_label_text;
  document.getElementById('verdictText').style.color = isHigh ? 'var(--red)' : 'var(--green)';
  document.getElementById('verdictProb').textContent = (prob * 100).toFixed(1) + '%';
  document.getElementById('verdictProb').style.color = isHigh ? 'var(--red)' : 'var(--green)';

  // Probability bar
  const fill = document.getElementById('probBarFill');
  fill.style.width    = (prob * 100).toFixed(1) + '%';
  fill.style.background = isHigh ? 'var(--red)' : 'var(--green)';

  const thLine = document.getElementById('probBarThreshold');
  thLine.style.left = (thresh * 100).toFixed(1) + '%';

  document.getElementById('thresholdLabel').textContent =
    'Umbral ' + (thresh * 100).toFixed(0) + '%';

  // Top features
  const feats = data.top_features || {};
  const maxImp = Math.max(...Object.values(feats), 0.0001);
  const list   = document.getElementById('featuresList');
  list.innerHTML = '';

  Object.entries(feats)
    .sort((a, b) => b[1] - a[1])
    .forEach(([name, imp]) => {
      const pct  = ((imp / maxImp) * 100).toFixed(0);
      const row  = document.createElement('div');
      row.className = 'feature-row';
      row.innerHTML = `
        <span class="feature-name" title="${name}">${name}</span>
        <div class="feature-bar-bg">
          <div class="feature-bar-fill" style="width:${pct}%"></div>
        </div>
        <span class="feature-pct">${(imp * 100).toFixed(1)}%</span>
      `;
      list.appendChild(row);
    });

  // Meta
  document.getElementById('metaInfo').textContent =
    `Modelo v${data.model_version} · Umbral ${thresh}`;
}
