/* eslint-disable no-console */
const API_BASE = window.API_BASE || 'http://localhost:5000';
const formatDate = (date) => date.toISOString().split('T')[0];

const clampNewsDate = (startDate) => {
  const today = new Date();
  const earliest = new Date();
  earliest.setDate(today.getDate() - 29);

  if (startDate > today) {
    return formatDate(today);
  }
  if (startDate < earliest) {
    return formatDate(earliest);
  }
  return formatDate(startDate);
};

const setStatus = (text, variant = 'idle') => {
  const badge = document.getElementById('status-badge');
  badge.textContent = text;
  badge.classList.remove('status--loading', 'status--error', 'status--done');
  if (variant === 'loading') badge.classList.add('status--loading');
  if (variant === 'error') badge.classList.add('status--error');
  if (variant === 'done') badge.classList.add('status--done');
};

const createChart = (ctx, label) =>
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label,
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.15)',
          tension: 0.3,
          data: [],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: '#94a3b8' },
        },
        y: {
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(148, 163, 184, 0.1)' },
        },
      },
      plugins: {
        legend: { labels: { color: '#f8fafc' } },
        tooltip: {
          callbacks: {
            label(ctx) {
              return `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} USD`;
            },
          },
        },
      },
    },
  });

const updateChart = (chart, labels, data, color = '#38bdf8') => {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  chart.data.datasets[0].borderColor = color;
  chart.update();
};

const renderNews = (articles) => {
  const list = document.getElementById('news-list');
  list.innerHTML = '';

  if (!articles.length) {
    const p = document.createElement('p');
    p.className = 'placeholder';
    p.textContent = 'Keine Artikel gefunden.';
    list.appendChild(p);
    return;
  }

  const formatter = new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  articles.slice(0, 10).forEach((article) => {
    const item = document.createElement('article');
    item.className = 'news-item';
    const title = document.createElement('h3');
    title.textContent = article.title || 'Unbenannter Artikel';
    const meta = document.createElement('p');
    const published = article.publishedAt ? formatter.format(new Date(article.publishedAt)) : 'unbekannt';
    meta.innerHTML = `<strong>${article.source?.name || 'Quelle unbekannt'}</strong> • ${published}`;
    const description = document.createElement('p');
    description.textContent = article.description || 'Keine Beschreibung verfügbar.';
    const link = document.createElement('a');
    link.href = article.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Zum Artikel';

    item.append(title, meta, description, link);
    list.appendChild(item);
  });
};

const deriveForecast = (records) => {
  if (!records.length) return { labels: [], values: [] };
  const closes = records.map((entry) => entry.close);
  const lastDate = new Date(records[records.length - 1].date);
  let avgDelta = 0;
  for (let i = 1; i < closes.length; i += 1) {
    avgDelta += closes[i] - closes[i - 1];
  }
  avgDelta /= Math.max(1, closes.length - 1);

  const labels = [];
  const values = [];
  let lastValue = closes[closes.length - 1];
  for (let day = 1; day <= 30; day += 1) {
    lastValue += avgDelta;
    const futureDate = new Date(lastDate);
    futureDate.setDate(lastDate.getDate() + day);
    labels.push(formatDate(futureDate));
    values.push(Number(lastValue.toFixed(2)));
  }
  return { labels, values };
};

const buildParams = (params) => new URLSearchParams(params).toString();

const fetchJson = async (url) => {
  const response = await fetch(`${API_BASE}${url}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Unbekannter Fehler beim Laden der Daten');
  }
  return data;
};

const attachInteractions = () => {
  const form = document.getElementById('control-form');
  const symbolSelect = document.getElementById('symbol');
  const startInput = document.getElementById('start-date');
  const endInput = document.getElementById('end-date');
  const resetBtn = document.getElementById('reset-btn');
  const refreshNewsBtn = document.getElementById('refresh-news');

  const today = new Date();
  const defaultStart = new Date();
  defaultStart.setDate(today.getDate() - 60);

  const oneYearAgo = new Date();
  oneYearAgo.setDate(today.getDate() - 365);
  const oneMonthAhead = new Date();
  oneMonthAhead.setDate(today.getDate() + 31);

  startInput.min = formatDate(oneYearAgo);
  startInput.max = formatDate(today);
  endInput.min = formatDate(oneYearAgo);
  endInput.max = formatDate(oneMonthAhead);
  startInput.value = formatDate(defaultStart);
  endInput.value = formatDate(today);

  const historicalChart = createChart(
    document.getElementById('historical-chart').getContext('2d'),
    'Historische Kurse',
  );
  const forecastChart = createChart(
    document.getElementById('forecast-chart').getContext('2d'),
    'Prognose (naiv)',
  );

  const state = {
    lastSymbol: symbolSelect.value,
    lastStart: startInput.value,
    lastEnd: endInput.value,
    historicalChart,
    forecastChart,
  };

  const runAnalysis = async (withNews = true) => {
    const symbol = symbolSelect.value;
    const start = startInput.value;
    const end = endInput.value;

    setStatus('Lade Kursdaten...', 'loading');
    try {
      const stockQuery = buildParams({ symbol, start, end });
      const stockData = await fetchJson(`/api/stocks/yf?${stockQuery}`);
      const labels = stockData.data.map((entry) => entry.date);
      const values = stockData.data.map((entry) => entry.close);
      updateChart(state.historicalChart, labels, values);

      const forecast = deriveForecast(stockData.data);
      updateChart(state.forecastChart, forecast.labels, forecast.values, '#a855f7');

      state.lastSymbol = symbol;
      state.lastStart = start;
      state.lastEnd = end;

      if (withNews) {
        await loadNews();
      } else {
        setStatus('Analyse abgeschlossen (ohne News)', 'done');
      }
    } catch (error) {
      console.error(error);
      setStatus(error.message, 'error');
    }
  };

  const loadNews = async () => {
    const symbol = state.lastSymbol;
    const startDate = new Date(state.lastStart);
    const newsFrom = clampNewsDate(startDate);

    setStatus('Lade News...', 'loading');
    try {
      const newsQuery = buildParams({ query: symbol, from: newsFrom });
      const newsData = await fetchJson(`/api/news?${newsQuery}`);
      renderNews(newsData.articles || []);
      setStatus('Analyse abgeschlossen', 'done');
    } catch (error) {
      console.error(error);
      setStatus(error.message, 'error');
    }
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    runAnalysis(true);
  });

  resetBtn.addEventListener('click', () => {
    symbolSelect.selectedIndex = 0;
    startInput.value = formatDate(defaultStart);
    endInput.value = formatDate(today);
    document.getElementById('news-list').innerHTML = '<p class="placeholder">Zurückgesetzt.</p>';
    updateChart(state.historicalChart, [], []);
    updateChart(state.forecastChart, [], [], '#a855f7');
    setStatus('Bereit', 'idle');
  });

  refreshNewsBtn.addEventListener('click', () => {
    if (!state.lastSymbol) {
      setStatus('Bitte zuerst eine Analyse starten', 'error');
      return;
    }
    loadNews();
  });

  // Erste Visualisierung beim Laden
  runAnalysis(true);
};

window.addEventListener('DOMContentLoaded', attachInteractions);
