/* Locally served dependencies only; never insert untrusted HTML. */
const canvas = document.getElementById('distribution');
if (canvas && window.Chart) {
  const values = JSON.parse(canvas.dataset.values);
  const palette = getComputedStyle(document.documentElement);
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: Object.keys(values).map(key => key.replaceAll('_', ' ')),
      datasets: [{
        label: 'Payout batches',
        data: Object.values(values),
        backgroundColor: palette.getPropertyValue('--brand-red').trim(),
        borderRadius: 3
      }]
    },
    options: {
      indexAxis: 'y',
      animation: false,
      maintainAspectRatio: false,
      responsive: true,
      plugins: {legend: {display: false}},
      scales: {
        x: {beginAtZero: true, ticks: {precision: 0}, grid: {color: '#ededed'}},
        y: {grid: {display: false}, ticks: {font: {size: 10}}}
      }
    }
  });
}
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', () => {
  const button = form.querySelector('button');
  // Named decision buttons must retain the submitted value.
  if (button && !button.name) {
    button.textContent = 'Processing…';
    button.setAttribute('aria-busy', 'true');
  }
}));
