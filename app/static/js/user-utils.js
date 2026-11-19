document.addEventListener("DOMContentLoaded", function () {
  const removeButtons = document.querySelectorAll(".remove-task, .remove-tag");

  removeButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();
      const form = button.closest("form");
      if (!form && !form.classList.contains("delete-form")) {
        return;
      }
      const message = button.classList.contains("remove-task")
        ? "Are you sure you want to delete this task?"
        : "Are you sure you want to delete this tag?";
      const confirmation = confirm(message);
      if (confirmation) {
        form.submit();
      }
    });
  });

  const colorItems = document.querySelectorAll("[data-color]");
  colorItems.forEach((colorItem) => {
    colorItem.style.color = colorItem.getAttribute("data-color");
  });

  const bgColorItems = document.querySelectorAll("[data-bg-color]");
  bgColorItems.forEach((bgColorItem) => {
    bgColorItem.style.backgroundColor =
      bgColorItem.getAttribute("data-bg-color");
  });
});
