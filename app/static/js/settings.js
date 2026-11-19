document.addEventListener("DOMContentLoaded", function () {
  const usernameInput = document.querySelector("#username");
  const originalUsername = usernameInput?.value;
  const emailInput = document.querySelector("#email");
  const originalEmail = emailInput?.value;
  const updateProfileBtn = document.getElementById("update-profile-btn");

  function unlockProfileUpdate(inputField, value) {
    updateProfileBtn.disabled = inputField.value === value;
  }

  if (usernameInput && originalUsername) {
    usernameInput.addEventListener("input", () => {
      unlockProfileUpdate(usernameInput, originalUsername);
    });
  }
  if (emailInput && originalEmail) {
    emailInput.addEventListener("input", () => {
      unlockProfileUpdate(emailInput, originalEmail);
    });
  }

  function confirmDelete() {
    const confirmed = confirm(
      "Are you sure you want to delete your account?\n\n" +
        "This action will:\n" +
        "- Delete all your tasks and tags\n" +
        "- Permanently remove your account\n" +
        "- Cannot be undone\n\n" +
        "Please confirm if you want to proceed."
    );

    if (confirmed) {
      // Double confirm
      return confirm(
        "Last chance: Are you absolutely sure you want to delete your account?"
      );
    }

    return false;
  }

  const deleteAccountForm = document.getElementById("delete-account-form");
  if (deleteAccountForm) {
    deleteAccountForm.addEventListener("submit", function (event) {
      if (!deleteAccountForm.checkValidity()) {
        return;
      }
      if (confirmDelete()) {
        deleteAccountForm.submit();
      }
    });
  }
});
