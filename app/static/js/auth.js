// Validation functions
const validateEmail = (email) => {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(email);
};

const validatePassword = (passwordField, validationForm) => {
  if (!validationForm) {
    return true;
  }

  let isValid = true;
  const password = passwordField.value;
  // const check = " ✔";
  // const cross = " ✖";
  const checkIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
  <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"/></svg>`;
  const crossIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
  <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/></svg>`;

  const specialChars = "!@#$%^&*()_-=[]{}|\\;:<>,.?/~+";

  const checks = {
    emojiAndAscii: {
      isValid: /^[\x00-\x7F]*$/.test(password),
      message: "Not containing any emoji or non-ASCII characters",
    },
    length: {
      isValid: password.length >= 8,
      message: "Be at least 8 characters long",
    },
    uppercase: {
      isValid: /[A-Z]/.test(password),
      message: "Contain at least one uppercase letter",
    },
    lowercase: {
      isValid: /[a-z]/.test(password),
      message: "Contain at least one lowercase letter",
    },
    number: {
      isValid: /[0-9]/.test(password),
      message: "Contain at least one number",
    },
    special: {
      isValid: /[!@#$%^&*()_\-=[\]{}|\\;:<>,.?/~+]/.test(password),
      message: `Contain at least one of the following special character:<br>${specialChars}`,
    },
    noSpaces: {
      isValid: !/\s/.test(password),
      message: "Not containing spaces",
    },
  };

  const showValidationInfo =
    passwordField?.getAttribute("validation-info") || "off";
  const passwordHelpDiv = validationForm?.querySelector(
    "#password-validation-info"
  );
  // console.log(passwordHelpDiv, showValidationInfo);
  if (showValidationInfo && passwordHelpDiv) {
    passwordHelpDiv.innerHTML = "";

    for (let requirement in checks) {
      const span = document.createElement("span");
      // span.className = "d-block";
      span.classList.add("password-requirements");
      //   span.classList.add("password-requirements"); d-flex align-items-center
      span.classList.add(
        checks[requirement].isValid ? "text-success" : "text-danger"
      );
      span.innerHTML = checks[requirement].message + " ";
      const requirementSpan = document.createElement("span");
      requirementSpan.className = "svg-icon";
      requirementSpan.innerHTML = checks[requirement].isValid
        ? checkIcon
        : crossIcon;
      span.appendChild(requirementSpan);
      passwordHelpDiv.appendChild(span);
    }
  }

  for (let requirement in checks) {
    if (!checks[requirement].isValid) {
      isValid = false;
      break;
    }
  }

  return isValid;
};

// Form validation setup
document.addEventListener("DOMContentLoaded", () => {
  const validationFields = [
    {
      id: "email",
    },
    {
      id: "username",
    },
    {
      id: "password",
    },
    {
      id: "password-confirmation",
    },
  ];

  const forms = document.querySelectorAll(".needs-validation");

  // Loop over them and prevent submission
  forms.forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add("was-validated");
      },
      false
    );
  });

  forms.forEach((form) => {
    const emailInput = form.querySelector(
      'input[type="email"][input-type="email"]'
    );
    const passwordInputs = form.querySelectorAll(
      'input[type="password"][password-input-type="password"]'
    );
    const confirmPasswordInput = form.querySelector(
      'input[type="password"][password-input-type="confirm"][bind-validation="true"]'
    );
    const usernameInput = form.querySelector(
      'input[name="text"][input-type="username"]'
    );
    // const submitButton = form.querySelector('button[type="submit"]');

    // Function to show error message
    const showError = (element, message) => {
      const errorDiv = element.nextElementSibling;
      const validationSpec = element.getAttribute("custom-validation") || "off";
      if (validationSpec !== "on") {
        return;
      }
      if (errorDiv && errorDiv.classList.contains("error-message")) {
        errorDiv.textContent = message;
        errorDiv.style.display = "block";
      } else {
        const div = document.createElement("div");
        div.className = "error-message";
        div.textContent = message;
        div.style.color = "red";
        div.style.fontSize = "0.8em";
        div.style.marginTop = "5px";
        element.parentNode.insertBefore(div, element.nextSibling);
      }
      element.classList.add("invalid");
    };

    // Function to hide error message
    const hideError = (element) => {
      const errorDiv = element.nextElementSibling;
      const validationSpec = element.getAttribute("custom-validation") || "off";
      if (validationSpec !== "on") {
        return;
      }
      if (errorDiv && errorDiv.classList.contains("error-message")) {
        errorDiv.style.display = "none";
      }
      element.classList.remove("invalid");
    };

    // Email validation
    const validateEmailInput = () => {
      const email = emailInput.value.trim();
      hideError(emailInput);
      if (email === "") {
        showError(emailInput, "Email is required");
        return false;
      }
      if (!validateEmail(email)) {
        showError(emailInput, "Please enter a valid email address");
        return false;
      }
      return true;
    };

    // Password validation
    const validatePasswordInput = (passwordField) => {
      const password = passwordField.value;
      const isValid = validatePassword(passwordField, form);
      hideError(passwordField);
      if (password === "") {
        showError(passwordField, "Password is required");
        return false;
      }
      if (!isValid) {
        showError(passwordField, "Invalid password");
        return false;
      }
      return true;
    };

    const validatePasswordConfirmation = () => {
      const bindPassword = form.querySelector(
        'input[type="password"][password-input-type="password"][bind-validation="true"]'
      );
      if (!bindPassword || !confirmPasswordInput) {
        if (!bindPassword) {
          console.error('No password input found with bind-validation="true"');
        }

        if (!confirmPasswordInput) {
          console.error(
            'No confirm password input found with bind-validation="true"'
          );
        }
        console.error(
          "No password validation across password fields are enabled."
        );

        return;
      }

      const password = bindPassword.value;
      const confirmPassword = confirmPasswordInput.value;
      hideError(confirmPasswordInput);
      if (confirmPassword === "") {
        showError(confirmPasswordInput, "Confirm password is required");
        return false;
      }
      if (password !== confirmPassword) {
        showError(confirmPasswordInput, "Passwords do not match");
        return false;
      }
      return true;
    };

    const validateUsernameInput = () => {
      const username = usernameInput.value.trim();
      hideError(usernameInput);
      if (username === "") {
        showError(usernameInput, "Username is required");
        return false;
      }
      return true;
    };

    const applyValidationEvents = (validationField, validationFunction) => {
      if (!validationField || !validationFunction) {
        return;
      }
      ["input", "change", "blur", "keydown"].forEach((event) => {
        validationField.addEventListener(event, validationFunction);
      });
    };

    // Add event listeners for real-time validation
    if (emailInput) {
      applyValidationEvents(emailInput, validateEmailInput);
      // ["input", "change", "blur", "keydown"].forEach((event) => {
      //   emailInput.addEventListener(event, validateEmailInput);
      // });
    }

    if (passwordInputs.length > 0) {
      passwordInputs.forEach((passwordInput) => {
        applyValidationEvents(passwordInput, () =>
          validatePasswordInput(passwordInput)
        );
      });
      // ["input", "change", "blur", "keydown"].forEach((event) => {
      //   passwordInput.addEventListener(event, validatePasswordInput);
      // });
    }

    if (confirmPasswordInput) {
      applyValidationEvents(confirmPasswordInput, validatePasswordConfirmation);
      // ["input", "change", "blur", "keydown"].forEach((event) => {
      //   confirmPasswordInput.addEventListener(
      //     event,
      //     validatePasswordConfirmation
      //   );
      // });
    }

    if (usernameInput) {
      applyValidationEvents(usernameInput, validateUsernameInput);
      // ["input", "change", "blur", "keydown"].forEach((event) => {
      //   usernameInput.addEventListener(event, validateUsernameInput);
      // });
    }

    // Form submission
    form.addEventListener("submit", (e) => {
      let isValid = true;

      if (emailInput) {
        isValid = validateEmailInput() && isValid;
      }

      if (passwordInputs.length > 0) {
        passwordInputs.forEach((passwordInput) => {
          isValid = validatePasswordInput(passwordInput) && isValid;
        });
      }

      if (confirmPasswordInput) {
        isValid = validatePasswordConfirmation() && isValid;
      }

      if (usernameInput) {
        isValid = validateUsernameInput() && isValid;
      }

      if (!isValid) {
        e.preventDefault();
      }
    });
  });
});
