document.addEventListener("DOMContentLoaded", function () {
  const mainFab = document.getElementById("main-fab");
  const fabMenu = document.getElementById("fab-menu");
  const createTask = document.getElementById("create-task");
  const createTag = document.getElementById("create-tag");
  const taskModal = document.getElementById("task-modal");
  const tagModal = document.getElementById("tag-modal");

  // Toggle FAB menu
  mainFab.addEventListener("click", () => {
    fabMenu.classList.toggle("active");
  });

  // Open task modal
  createTask.addEventListener("click", () => {
    taskModal.classList.add("active");
    fabMenu.classList.remove("active");
  });

  // Open tag modal
  createTag.addEventListener("click", () => {
    tagModal.classList.add("active");
    fabMenu.classList.remove("active");
  });

  // Close modals
  document.querySelectorAll("[data-modal-close]").forEach((button) => {
    button.addEventListener("click", () => {
      const modalId = button.getAttribute("data-modal-close");
      document.getElementById(modalId).classList.remove("active");
    });
  });

  // Close modal when clicking outside
  document.querySelectorAll(".create-modal").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });
  });

  const taskTags = document.getElementById("task-tags");
  // const userId = sessionStorage.getItem("user_id");

  fetch(`/api/user/tags`)
    .then((response) => response.json())
    .then((tags) => {
      tags.forEach((tag) => {
        const option = document.createElement("option");
        option.value = tag.id;
        option.text = tag.name;
        option.style.color = tag.color;
        taskTags.add(option);
      });
    })
    .catch((error) => console.error(error));
});
