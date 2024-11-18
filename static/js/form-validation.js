async function isTagExists(tag) {
  const response = await fetch(`/api/user/tags/search?tag=${tag}`);
  const data = await response.json();
  return data.count == 1;
}

document.addEventListener("DOMContentLoaded", () => {
  const tagNameInput = document.getElementById("tag-name");

  if (tagNameInput) {
    tagNameInput.oninput = async function () {
      const tag = tagNameInput.value;
      const tagNameFeedbackDiv = tagNameInput.nextSibling;
      // console.log(isTagExists(tag));
      if (await isTagExists(tag)) {
        tagNameFeedbackDiv.textContent = "Tag already exist";
        tagNameFeedbackDiv.style.display = "block";
      } else {
        tagNameFeedbackDiv.textContent = "";
        tagNameFeedbackDiv.style.display = "none";
      }
    };
  }

  const validationFields = [
    {
      id: "task-title",
      //   isRequired: true,
      message: "Please provide a task title.",
    },
    {
      id: "task-priority",
      message: "Please set a task priority.",
    },
    {
      id: "task-status",
      message: "Please set a task status.",
    },
    {
      id: "tag-name",
      message: "Please provide a tag title.",
    },
  ];

  validationFields.forEach((field) => {
    const element = document.getElementById(field.id);
    if (!element) {
      return;
    }
    element.required = true;
    const feedback = document.createElement("div");
    feedback.className = "invalid-feedback";
    feedback.innerText = field.message;
    element.parentNode.insertBefore(feedback, element.nextSibling);
  });

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll(".needs-validation");

  // Loop over them and prevent submission
  if (forms) {
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
  }
});
