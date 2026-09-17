"use strict";

const state = {
  user: null,
  csrfToken: "",
  tasks: [],
  authMode: "login",
  draggedTaskId: null,
};

const selectors = {
  authView: document.querySelector("#auth-view"),
  appView: document.querySelector("#app-view"),
  authForm: document.querySelector("#auth-form"),
  authError: document.querySelector("#auth-error"),
  authTitle: document.querySelector("#auth-title"),
  authSubtitle: document.querySelector("#auth-subtitle"),
  authSubmit: document.querySelector("#auth-submit"),
  authSwitch: document.querySelector("#auth-switch"),
  switchCopy: document.querySelector("#switch-copy"),
  nameField: document.querySelector("#name-field"),
  displayName: document.querySelector("#display-name"),
  email: document.querySelector("#email"),
  password: document.querySelector("#password"),
  demoLogin: document.querySelector("#demo-login"),
  search: document.querySelector("#search"),
  priorityFilter: document.querySelector("#priority-filter"),
  taskDialog: document.querySelector("#task-dialog"),
  taskForm: document.querySelector("#task-form"),
  taskError: document.querySelector("#task-error"),
  toast: document.querySelector("#toast"),
  activityList: document.querySelector("#activity-list"),
};

async function request(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  if (state.csrfToken && ["POST", "PUT", "DELETE"].includes(options.method)) {
    headers["X-CSRF-Token"] = state.csrfToken;
  }
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || `Ошибка ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return payload;
}

function showToast(message, isError = false) {
  selectors.toast.textContent = message;
  selectors.toast.classList.toggle("error", isError);
  selectors.toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => selectors.toast.classList.remove("visible"), 2600);
}

function showAuth() {
  state.user = null;
  state.csrfToken = "";
  selectors.appView.hidden = true;
  selectors.authView.hidden = false;
}

async function showApp(session) {
  state.user = session.user;
  state.csrfToken = session.csrf_token;
  selectors.authView.hidden = true;
  selectors.appView.hidden = false;
  document.querySelector("#profile-name").textContent = state.user.display_name;
  document.querySelector("#profile-email").textContent = state.user.email;
  document.querySelector("#profile-avatar").textContent = state.user.display_name.slice(0, 1).toUpperCase();
  await refreshBoard();
}

function setAuthMode(mode) {
  state.authMode = mode;
  const register = mode === "register";
  selectors.nameField.hidden = !register;
  selectors.displayName.required = register;
  selectors.password.autocomplete = register ? "new-password" : "current-password";
  selectors.authTitle.textContent = register ? "Создать аккаунт" : "Вход в FlowBoard";
  selectors.authSubtitle.textContent = register
    ? "Начните с чистой доски за минуту"
    : "Продолжите работу со своей доской";
  selectors.authSubmit.textContent = register ? "Создать аккаунт" : "Войти";
  selectors.switchCopy.textContent = register ? "Уже есть аккаунт?" : "Нет аккаунта?";
  selectors.authSwitch.textContent = register ? "Войти" : "Создать";
  selectors.authError.textContent = "";
}

selectors.authSwitch.addEventListener("click", () => {
  setAuthMode(state.authMode === "login" ? "register" : "login");
});

selectors.authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  selectors.authError.textContent = "";
  selectors.authSubmit.disabled = true;
  const payload = { email: selectors.email.value, password: selectors.password.value };
  if (state.authMode === "register") payload.display_name = selectors.displayName.value;
  try {
    const session = await request(`/api/${state.authMode}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    await showApp(session);
  } catch (error) {
    selectors.authError.textContent = error.message;
  } finally {
    selectors.authSubmit.disabled = false;
  }
});

selectors.demoLogin.addEventListener("click", async () => {
  setAuthMode("login");
  selectors.email.value = "demo@example.com";
  selectors.password.value = "Demo123!";
  selectors.demoLogin.disabled = true;
  try {
    const session = await request("/api/login", {
      method: "POST",
      body: JSON.stringify({ email: selectors.email.value, password: selectors.password.value }),
    });
    await showApp(session);
  } catch (error) {
    selectors.authError.textContent = error.message;
  } finally {
    selectors.demoLogin.disabled = false;
  }
});

document.querySelector("#logout").addEventListener("click", async () => {
  try { await request("/api/logout", { method: "POST", body: "{}" }); } catch (_) { /* cookie is cleared client-side by reload */ }
  showAuth();
  selectors.authForm.reset();
});

async function refreshBoard() {
  const params = new URLSearchParams();
  if (selectors.search.value.trim()) params.set("query", selectors.search.value.trim());
  if (selectors.priorityFilter.value) params.set("priority", selectors.priorityFilter.value);
  try {
    const [taskData, statsData, activityData] = await Promise.all([
      request(`/api/tasks?${params}`),
      request("/api/stats"),
      request("/api/activity"),
    ]);
    state.tasks = taskData.tasks;
    renderBoard();
    renderStats(statsData.stats);
    renderActivity(activityData.activity);
  } catch (error) {
    if (error.status === 401) showAuth();
    else showToast(error.message, true);
  }
}

function renderBoard() {
  const statuses = ["backlog", "in_progress", "done"];
  statuses.forEach((status) => {
    const list = document.querySelector(`[data-list="${status}"]`);
    list.replaceChildren();
    const tasks = state.tasks.filter((task) => task.status === status);
    document.querySelector(`[data-count="${status}"]`).textContent = tasks.length;
    if (!tasks.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = status === "backlog" ? "Здесь появятся новые идеи" : "Переместите сюда задачу";
      list.append(empty);
    } else {
      tasks.forEach((task) => list.append(createTaskCard(task)));
    }
  });
}

function createTaskCard(task) {
  const card = document.createElement("article");
  card.className = "task-card";
  card.draggable = true;
  card.dataset.id = task.id;
  card.addEventListener("dragstart", () => {
    state.draggedTaskId = task.id;
    card.classList.add("dragging");
  });
  card.addEventListener("dragend", () => {
    state.draggedTaskId = null;
    card.classList.remove("dragging");
  });

  const header = document.createElement("div");
  header.className = "task-card-header";
  const headingWrap = document.createElement("div");
  headingWrap.style.flex = "1";
  const priority = document.createElement("span");
  priority.className = `priority priority-${task.priority}`;
  priority.textContent = { high: "высокий", medium: "средний", low: "низкий" }[task.priority];
  const title = document.createElement("h3");
  title.textContent = task.title;
  headingWrap.append(priority, title);
  const edit = document.createElement("button");
  edit.className = "card-edit";
  edit.type = "button";
  edit.setAttribute("aria-label", `Изменить ${task.title}`);
  edit.textContent = "•••";
  edit.addEventListener("click", () => openTaskDialog(task));
  header.append(headingWrap, edit);
  card.append(header);

  if (task.description) {
    const description = document.createElement("p");
    description.textContent = task.description;
    card.append(description);
  }
  const meta = document.createElement("div");
  meta.className = "task-meta";
  const due = document.createElement("span");
  due.className = "due";
  if (task.due_date) {
    const overdue = task.status !== "done" && task.due_date < new Date().toISOString().slice(0, 10);
    due.classList.toggle("overdue", overdue);
    due.textContent = `${overdue ? "⚠ " : ""}до ${formatDate(task.due_date)}`;
  } else {
    due.textContent = "без срока";
  }
  const moves = document.createElement("div");
  moves.className = "move-actions";
  const statusIndex = ["backlog", "in_progress", "done"].indexOf(task.status);
  if (statusIndex > 0) moves.append(moveButton(task, ["backlog", "in_progress", "done"][statusIndex - 1], "←", "На предыдущий этап"));
  if (statusIndex < 2) moves.append(moveButton(task, ["backlog", "in_progress", "done"][statusIndex + 1], "→", "На следующий этап"));
  meta.append(due, moves);
  card.append(meta);
  return card;
}

function moveButton(task, status, label, ariaLabel) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.setAttribute("aria-label", ariaLabel);
  button.addEventListener("click", () => moveTask(task, status));
  return button;
}

document.querySelectorAll(".column").forEach((column) => {
  column.addEventListener("dragover", (event) => { event.preventDefault(); column.classList.add("is-over"); });
  column.addEventListener("dragleave", () => column.classList.remove("is-over"));
  column.addEventListener("drop", async (event) => {
    event.preventDefault();
    column.classList.remove("is-over");
    const task = state.tasks.find((item) => item.id === state.draggedTaskId);
    if (task && task.status !== column.dataset.status) await moveTask(task, column.dataset.status);
  });
});

async function moveTask(task, status) {
  try {
    await request(`/api/tasks/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({ status, version: task.version }),
    });
    showToast("Статус задачи обновлён");
    await refreshBoard();
  } catch (error) { showToast(error.message, true); }
}

function renderStats(stats) {
  document.querySelector("#stat-total").textContent = stats.total;
  document.querySelector("#stat-progress").textContent = stats.in_progress;
  document.querySelector("#stat-done").textContent = stats.done;
  document.querySelector("#stat-overdue").textContent = stats.overdue;
}

function renderActivity(activity) {
  selectors.activityList.replaceChildren();
  const actionNames = {
    registered: "Создан аккаунт",
    demo_seeded: "Демо-данные готовы",
    task_created: "Задача создана",
    task_updated: "Задача изменена",
    task_moved: "Задача перемещена",
    task_deleted: "Задача удалена",
  };
  activity.forEach((item) => {
    const row = document.createElement("li");
    const copy = document.createElement("span");
    const action = document.createElement("strong");
    action.textContent = actionNames[item.action] || item.action;
    copy.append(action, document.createTextNode(item.details ? ` · ${item.details}` : ""));
    const time = document.createElement("time");
    time.textContent = formatTimestamp(item.created_at);
    row.append(copy, time);
    selectors.activityList.append(row);
  });
}

function openTaskDialog(task = null, status = "backlog") {
  selectors.taskForm.reset();
  selectors.taskError.textContent = "";
  document.querySelector("#task-id").value = task?.id || "";
  document.querySelector("#task-version").value = task?.version || "";
  document.querySelector("#task-title").value = task?.title || "";
  document.querySelector("#task-description").value = task?.description || "";
  document.querySelector("#task-status").value = task?.status || status;
  document.querySelector("#task-priority").value = task?.priority || "medium";
  document.querySelector("#task-due").value = task?.due_date || "";
  document.querySelector("#dialog-title").textContent = task ? "Изменить задачу" : "Новая задача";
  document.querySelector("#delete-task").hidden = !task;
  selectors.taskDialog.showModal();
  window.setTimeout(() => document.querySelector("#task-title").focus(), 0);
}

document.querySelector("#new-task").addEventListener("click", () => openTaskDialog());
document.querySelectorAll("[data-add-status]").forEach((button) => button.addEventListener("click", () => openTaskDialog(null, button.dataset.addStatus)));
document.querySelector("#dialog-close").addEventListener("click", () => selectors.taskDialog.close());
document.querySelector("#task-cancel").addEventListener("click", () => selectors.taskDialog.close());

selectors.taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = document.querySelector("#task-id").value;
  const payload = {
    title: document.querySelector("#task-title").value,
    description: document.querySelector("#task-description").value,
    status: document.querySelector("#task-status").value,
    priority: document.querySelector("#task-priority").value,
    due_date: document.querySelector("#task-due").value || null,
  };
  if (id) payload.version = Number(document.querySelector("#task-version").value);
  try {
    await request(id ? `/api/tasks/${id}` : "/api/tasks", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    selectors.taskDialog.close();
    showToast(id ? "Задача обновлена" : "Задача создана");
    await refreshBoard();
  } catch (error) { selectors.taskError.textContent = error.message; }
});

document.querySelector("#delete-task").addEventListener("click", async () => {
  const id = document.querySelector("#task-id").value;
  if (!id || !window.confirm("Удалить эту задачу?")) return;
  try {
    await request(`/api/tasks/${id}`, { method: "DELETE", body: "{}" });
    selectors.taskDialog.close();
    showToast("Задача удалена");
    await refreshBoard();
  } catch (error) { selectors.taskError.textContent = error.message; }
});

let filterTimer;
selectors.search.addEventListener("input", () => {
  window.clearTimeout(filterTimer);
  filterTimer = window.setTimeout(refreshBoard, 250);
});
selectors.priorityFilter.addEventListener("change", refreshBoard);

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "short" }).format(new Date(`${value}T12:00:00`));
}

function formatTimestamp(value) {
  return new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(`${value.replace(" ", "T")}Z`));
}

async function bootstrap() {
  try {
    const session = await request("/api/session");
    if (session.authenticated) await showApp(session);
    else showAuth();
  } catch (_) { showAuth(); }
}

bootstrap();
