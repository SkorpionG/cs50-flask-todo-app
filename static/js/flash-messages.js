// Handle auto-dismiss effects for flash messages
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss flash messages after 5 seconds
  const flashMessages = document.querySelectorAll(".alert");
  flashMessages.forEach(function (flash) {
    if (flash.classList.contains("alert-static")) {
      return; // Skip static flash messages
    }
    setTimeout(function () {
      flash.classList.add("fade-out");
      setTimeout(function () {
        flash.remove();
      }, 300); // Match this with your CSS animation duration
    }, 5000);

    // Close button handler
    const closeButton = flash.querySelector(".btn-close");
    if (closeButton) {
      closeButton.addEventListener("click", function () {
        flash.classList.add("fade-out");
        setTimeout(function () {
          flash.remove();
        }, 300);
      });
    }
  });
});
