const API_URL = "/api/todos";
const form = document.querySelector("#todo-form");
const titleInput = document.querySelector("#todo-title");
const descriptionInput = document.querySelector("#todo-description");
const todoList = document.querySelector("#todo-list");
const message = document.querySelector("#message");

async function requestTodos(url = API_URL, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || "Something went wrong. Please try again.");
  }
  return response.status === 204 ? null : response.json();
}

function renderTodos(todos) {
  todoList.replaceChildren();

  if (todos.length === 0) {
    const emptyState = document.createElement("li");
    emptyState.textContent = "No tasks yet. Add one above.";
    todoList.append(emptyState);
    return;
  }

  todos.forEach((todo) => {
    const item = document.createElement("li");
    const title = document.createElement("span");
    title.className = `task-title${todo.completed ? " completed" : ""}`;
    title.textContent = todo.title;
    const taskContent = document.createElement("div");
    taskContent.className = "task-content";
    const description = document.createElement("p");
    description.className = "task-description";
    description.textContent = todo.description;

    const actions = document.createElement("span");
    actions.className = "task-actions";

    const toggleButton = document.createElement("button");
    toggleButton.type = "button";
    toggleButton.textContent = todo.completed ? "Undo" : "Complete";
    toggleButton.addEventListener("click", () => updateTodo(todo.id));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => removeTodo(todo.id));

    actions.append(toggleButton, deleteButton);
    taskContent.append(title, description);
    item.append(taskContent, actions);
    todoList.append(item);
  });
}

async function loadTodos() {
  try {
    message.textContent = "";
    renderTodos(await requestTodos());
  } catch (error) {
    message.textContent = error.message;
  }
}

async function updateTodo(id) {
  try {
    message.textContent = "";
    await requestTodos(`${API_URL}/${id}`, { method: "PATCH" });
    await loadTodos();
  } catch (error) {
    message.textContent = error.message;
  }
}

async function removeTodo(id) {
  try {
    message.textContent = "";
    await requestTodos(`${API_URL}/${id}`, { method: "DELETE" });
    await loadTodos();
  } catch (error) {
    message.textContent = error.message;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();
  if (!title || !description) return;

  try {
    message.textContent = "";
    await requestTodos(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemName: title, itemDescription: description }),
    });
    window.location.assign("/success.html");
  } catch (error) {
    message.textContent = error.message;
  }
});

loadTodos();
