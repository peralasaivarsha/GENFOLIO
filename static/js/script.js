document.addEventListener("DOMContentLoaded", function () {

  // Add this at the beginning of your DOMContentLoaded event
if (document.getElementById('authStatus')) {
  fetch('/check_auth')
      .then(response => response.json())
      .then(data => {
          const authStatus = document.getElementById('authStatus');
          if (data.authenticated) {
              authStatus.innerHTML = `
                  <span class="text-success">Logged in as ${data.username}</span>
                  <a href="/logout" class="btn btn-sm btn-outline-danger ms-2">Logout</a>
              `;
          } else {
              authStatus.innerHTML = `
                  <a href="/login" class="btn btn-sm btn-outline-primary me-2">Login</a>
                  <a href="/register" class="btn btn-sm btn-outline-secondary">Register</a>
              `;
          }
      });
}
  // Portfolio type selection handling
  const portfolioTypeBtns = document.querySelectorAll(".portfolio-type-btn");
  const businessForm = document.getElementById("businessForm");
  const educationForm = document.getElementById("educationForm");
  const portfolioTypeSelection = document.getElementById(
    "portfolioTypeSelection"
  );

  // Active form elements
  let activeForm = null;
  let activePreviewContainer = null;
  let activePlaceholder = null;
  let activePortfolioPreview = null;
  let activeTemplateInfo = null;

  // Buttons - now using class selectors instead of IDs
  const toggleThemeBtns = document.querySelectorAll('[id$="ToggleThemeBtn"]');
  const regenerateBtns = document.querySelectorAll('[id$="RegenerateBtn"]');
  const downloadBtns = document.querySelectorAll('[id$="DownloadBtn"]');

  // State variables
  let currentPortfolioData = null;
  let currentTheme = "light";
  let currentDownloadPath = "";

  // Handle portfolio type selection
  portfolioTypeBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const type = this.getAttribute("data-type");
      portfolioTypeSelection.classList.add("d-none");

      if (type === "business") {
        businessForm.classList.remove("d-none");
        educationForm.classList.add("d-none");
        activeForm = businessForm.querySelector("#portfolioForm");
        activePreviewContainer =
          businessForm.querySelector("#previewContainer");
        activePlaceholder = businessForm.querySelector("#placeholder");
        activePortfolioPreview =
          businessForm.querySelector("#portfolioPreview");
        activeTemplateInfo = businessForm.querySelector("#templateInfo");
      } else {
        educationForm.classList.remove("d-none");
        businessForm.classList.add("d-none");
        activeForm = educationForm.querySelector("#portfolioForm");
        activePreviewContainer =
          educationForm.querySelector("#previewContainer");
        activePlaceholder = educationForm.querySelector("#placeholder");
        activePortfolioPreview =
          educationForm.querySelector("#portfolioPreview");
        activeTemplateInfo = educationForm.querySelector("#templateInfo");
      }
    });
  });

  // Form submission handling
  const forms = document.querySelectorAll("#portfolioForm");
  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      generatePortfolio();
    });
  });

  // Toggle theme buttons
  toggleThemeBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      if (currentPortfolioData) {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        generatePortfolio();
      }
    });
  });

  // Regenerate buttons
  regenerateBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      if (currentPortfolioData) {
        generatePortfolio();
      }
    });
  });

  // Download buttons
  downloadBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      if (currentDownloadPath) {
        window.location.href = `/download?path=${encodeURIComponent(
          currentDownloadPath
        )}`;
      }
    });
  });


  // Add Experience Field
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-experience")) {
      const container = document.getElementById("experienceContainer");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <textarea class="form-control" name="experience[]"></textarea>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Add Skill Field
    if (e.target.classList.contains("add-skill")) {
      const container = document.getElementById("skillsContainer");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <input type="text" class="form-control" name="skills[]">
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Add Achievement Field
    if (e.target.classList.contains("add-achievement")) {
      const container = document.getElementById("achievementsContainer");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <textarea class="form-control" name="achievements[]"></textarea>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Remove Field
    if (e.target.classList.contains("remove-field")) {
      e.target.closest(".input-group").remove();
    }
  });



  // Event delegation for all dynamic field operations
document.addEventListener("click", function (e) {
    // Add Education Field
    if (e.target.classList.contains("add-education")) {
      const container = document.getElementById("educationContainer");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <textarea class="form-control" name="education[]" required></textarea>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Add Skill Field
    if (e.target.classList.contains("add-skilleducation")) {
      const container = document.getElementById("skillsContainereducation");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <input type="text" class="form-control" name="skillseducation[]" required>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Add Project Field
    if (e.target.classList.contains("add-project")) {
      const container = document.getElementById("projectsContainer");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <textarea class="form-control" name="projects[]" required></textarea>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Add Achievement Field
    if (e.target.classList.contains("add-achievementeducation")) {
      const container = document.getElementById("achievementsContainereducation");
      const newField = document.createElement("div");
      newField.className = "input-group mb-2";
      newField.innerHTML = `
            <textarea class="form-control" name="achievementseducation[]"></textarea>
            <button type="button" class="btn btn-outline-danger remove-field">
                <i class="fas fa-minus"></i>
            </button>
        `;
      container.appendChild(newField);
    }

    // Remove Field
    if (e.target.classList.contains("remove-field")) {
      e.target.closest(".input-group").remove();
    }
});

async function generatePortfolio() {
    if (!activeForm) return;

    // Create proper FormData object
    const formData = new FormData(activeForm);

    // Add all form data
    formData.append(
      "portfolioType",
      activeForm.querySelector("#portfolioType").value
    );
    formData.append("name", activeForm.querySelector("#name").value);
    formData.append("email", activeForm.querySelector("#email").value);
    formData.append("style", activeForm.querySelector("#style").value);
    formData.append(
      "theme",
      activeForm.querySelector('input[name="theme"]:checked').value
    );

    // Handle file upload
    const profilePicInput = activeForm.querySelector("#profilePic");
    if (profilePicInput.files.length > 0) {
      formData.append("profilePic", profilePicInput.files[0]);
    }

    // Add social links
    const linkedin = activeForm.querySelector("#linkedin").value || "#";
    const github = activeForm.querySelector("#github").value || "#";
    const resume = activeForm.querySelector("#resume").value || "#";
    formData.append("linkedin", linkedin);
    formData.append("github", github);
    formData.append("resume", resume);

    // Add portfolio type specific fields
    if (formData.get("portfolioType") === "business") {
      formData.append("company", activeForm.querySelector("#company").value);
      formData.append("position", activeForm.querySelector("#position").value);

      // Handle multiple experience fields
      const experienceFields = activeForm.querySelectorAll(
        'textarea[name="experience[]"]'
      );
      experienceFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("experience", field.value);
        }
      });

      // Handle multiple skills fields
      const skillsFields = activeForm.querySelectorAll(
        'input[name="skills[]"]'
      );
      skillsFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("skills", field.value);
        }
      });

      // Handle multiple achievements fields
      const achievementsFields = activeForm.querySelectorAll(
        'textarea[name="achievements[]"]'
      );
      achievementsFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("achievements", field.value);
        }
      });
      const twitter = activeForm.querySelector("#twitter").value || "#";
      formData.append("twitter", twitter);
    } 
    else 
    {
      // Handle multiple education fields
      const educationFields = activeForm.querySelectorAll(
        'textarea[name="education[]"]'
      );
      educationFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("education", field.value);
          console.log(field.value);
        }
      });
      console.log(formData["education"]);

      // Handle multiple skills fields
      const skillsFields = activeForm.querySelectorAll(
        'input[name="skillseducation[]"]'
      );
      skillsFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("skills", field.value);
        }
      });

      // Handle multiple projects fields
      const projectsFields = activeForm.querySelectorAll(
        'textarea[name="projects[]"]'
      );
      projectsFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("projects", field.value);
        }
      });

      // Handle multiple achievements fields
      const achievementsFields = activeForm.querySelectorAll(
        'textarea[name="achievementseducation[]"]'
      );
      achievementsFields.forEach((field) => {
        if (field.value.trim() !== "") {
          formData.append("achievements", field.value);
        }
      });
    }
    console.log(formData["achievements"]);
    console.log(formData["projects"]);
    console.log(formData["skills"]);

    // Store the data (excluding the file)
    currentPortfolioData = Object.fromEntries(formData.entries());

    // Show loading state
    if (activePortfolioPreview) {
      activePortfolioPreview.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Generating your portfolio...</p>
            </div>
        `;
    }

    if (activePreviewContainer)
      activePreviewContainer.classList.remove("d-none");
    if (activePlaceholder) activePlaceholder.classList.add("d-none");

    // Send to server - DON'T set Content-Type header!
    fetch("/generate", {
      method: "POST",
      body: formData, // Let browser set headers automatically
    })
    .then(response => {
      // First check if the response is OK
      if (!response.ok) {
          return response.text().then(text => {
              throw new Error(text || 'Server error');
          });
      }
      return response.json();
  })
      .then((data) => {
        if (data.success) {
          if (activePortfolioPreview) {
            activePortfolioPreview.innerHTML = data.preview;
          }
          currentDownloadPath = data.download_path;
          if (activeTemplateInfo) {
            activeTemplateInfo.textContent = `Template used: ${data.template_used}`;
          }

          // Update theme radio button
          const themeRadioId =
            formData.get("portfolioType") === "business"
              ? `${data.theme}Theme`
              : `${data.theme}ThemeEdu`;
          const themeRadio = document.getElementById(themeRadioId);
          if (themeRadio) themeRadio.checked = true;
        } else {
          showError(data.error || "Failed to generate portfolio");
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        showError(error.message || "An error occurred");
      });
  }


  function showError(message) {
    if (activePortfolioPreview) {
      activePortfolioPreview.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${message}
                </div>
            `;
    }
  }
});
