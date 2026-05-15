let tasks = [];
let nextId = 1;
const deletingIds = new Set();
const history = [];

function formatTime(date) {
  return date.toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
  });
}

function addTask(text) {
  const id = nextId++;
  const createdAt = new Date();
  tasks.push({ id, text, createdAt });
  history.unshift({ id, text, createdAt, deletedAt: null });
  render();
  renderHistory();
}

function startDelete(id) {
  deletingIds.add(id);
  render();
  setTimeout(() => {
    tasks = tasks.filter(t => t.id !== id);
    deletingIds.delete(id);
    const entry = history.find(h => h.id === id);
    if (entry) entry.deletedAt = new Date();
    render();
    renderHistory();
  }, 1100);
}

function render() {
  const list = document.getElementById('task-list');
  list.innerHTML = '';

  if (tasks.length === 0) {
    list.innerHTML = '<li class="empty-msg">No tasks yet. Add one above!</li>';
    return;
  }

  tasks.forEach(task => {
    const li = document.createElement('li');
    if (deletingIds.has(task.id)) li.classList.add('deleting');

    const content = document.createElement('div');
    content.className = 'task-content';

    const textSpan = document.createElement('span');
    textSpan.className = 'task-text';
    textSpan.textContent = task.text;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'task-time';
    timeSpan.textContent = 'Added ' + formatTime(task.createdAt);

    content.appendChild(textSpan);
    content.appendChild(timeSpan);

    const btn = document.createElement('button');
    btn.textContent = 'Delete';
    btn.className = 'delete-btn';
    btn.addEventListener('click', () => startDelete(task.id));

    li.appendChild(content);
    li.appendChild(btn);
    list.appendChild(li);
  });
}

function renderHistory() {
  const container = document.getElementById('history-list');
  container.innerHTML = '';

  if (history.length === 0) {
    container.innerHTML = '<p class="history-empty">No tasks recorded yet.</p>';
    return;
  }

  const table = document.createElement('table');
  table.className = 'history-table';

  const thead = document.createElement('thead');
  thead.innerHTML = '<tr><th>Task</th><th>Created</th><th>Deleted</th></tr>';
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  history.forEach(entry => {
    const tr = document.createElement('tr');
    if (entry.deletedAt) tr.classList.add('was-deleted');

    const tdName = document.createElement('td');
    tdName.className = 'h-task';
    tdName.textContent = entry.text;

    const tdCreated = document.createElement('td');
    tdCreated.className = 'h-time';
    tdCreated.textContent = formatTime(entry.createdAt);

    const tdDeleted = document.createElement('td');
    tdDeleted.className = 'h-time';
    if (entry.deletedAt) {
      tdDeleted.textContent = formatTime(entry.deletedAt);
    } else {
      const badge = document.createElement('span');
      badge.className = 'active-badge';
      badge.textContent = 'Active';
      tdDeleted.appendChild(badge);
    }

    tr.appendChild(tdName);
    tr.appendChild(tdCreated);
    tr.appendChild(tdDeleted);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  container.appendChild(table);
}

function openHistory() {
  document.getElementById('history-panel').classList.add('open');
  document.getElementById('overlay').classList.add('visible');
}

function closeHistory() {
  document.getElementById('history-panel').classList.remove('open');
  document.getElementById('overlay').classList.remove('visible');
}

document.getElementById('menu-btn').addEventListener('click', openHistory);
document.getElementById('close-btn').addEventListener('click', closeHistory);
document.getElementById('overlay').addEventListener('click', closeHistory);

document.getElementById('task-form').addEventListener('submit', e => {
  e.preventDefault();
  const input = document.getElementById('task-input');
  const text = input.value.trim();
  if (text) {
    addTask(text);
    input.value = '';
  }
});

render();
renderHistory();
