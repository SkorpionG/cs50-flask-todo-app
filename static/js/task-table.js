dayjs.extend(window.dayjs_plugin_customParseFormat);

class TaskTable {
  constructor(container) {
    this.container = container;
    this.settingKey = "taskTablePreferences";
    this.setupEventListeners();
    this.loadSavedPreferences();
    this.setupTagFiltering();
  }

  // static resetSettings() {
  //   localStorage.removeItem(this.settingKey);
  //   const taskTable = document.querySelector("#task-table");
  //   if (taskTable) {
  //     const taskTableInstance = new TaskTable(taskTable);
  //     taskTableInstance.loadSavedPreferences();
  //   }
  // }

  static clearSettings() {
    localStorage.removeItem(this.settingKey);
  }

  setupTagFiltering() {
    // Prevent dropdown from closing when clicking inside
    const tagFilterMenu = this.container.querySelector("#tag-filter-menu");
    if (tagFilterMenu) {
      tagFilterMenu.addEventListener("click", (e) => {
        e.stopPropagation();
      });

      // Setup select/clear all buttons
      const selectAllBtn = tagFilterMenu.querySelector("#select-all-tags");
      const clearAllBtn = tagFilterMenu.querySelector("#clear-all-tags");

      if (selectAllBtn) {
        selectAllBtn.addEventListener("click", () => {
          const checkboxes = tagFilterMenu.querySelectorAll(
            ".tag-filter-checkbox"
          );
          checkboxes.forEach((cb) => (cb.checked = true));
          this.applyFilters();
        });
      }

      if (clearAllBtn) {
        clearAllBtn.addEventListener("click", () => {
          const checkboxes = tagFilterMenu.querySelectorAll(
            ".tag-filter-checkbox"
          );
          checkboxes.forEach((cb) => (cb.checked = false));
          this.applyFilters();
        });
      }

      // Setup individual checkboxes
      const checkboxes = tagFilterMenu.querySelectorAll(".tag-filter-checkbox");
      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
          this.applyFilters();
          this.updateTagFilterIndicator();
        });
      });
    }
  }

  updateTagFilterIndicator() {
    const dropdown = this.container.querySelector("#tag-filter-dropdown");
    const checkboxes = this.container.querySelectorAll(".tag-filter-checkbox");
    const hasSelected = Array.from(checkboxes).some((cb) => cb.checked);

    if (dropdown) {
      dropdown.classList.toggle("has-selected", hasSelected);
    }
  }

  toggleSortDirection() {
    const sortButton = this.container.querySelector("#sort-direction");
    const newDirection =
      sortButton.dataset.direction === "asc" ? "desc" : "asc";
    sortButton.dataset.direction = newDirection;
    this.updateSortIcon(sortButton, newDirection);
  }

  setupEventListeners() {
    // Filtering
    const searchInput = this.container.querySelector("#search-input");
    const statusFilter = this.container.querySelector("#status-filter");
    const priorityFilter = this.container.querySelector("#priority-filter");
    const dateFilter = this.container.querySelector("#date-filter");

    // Add event listeners for filters
    [searchInput, statusFilter, priorityFilter, dateFilter].forEach(
      (element) => {
        if (element) {
          element.addEventListener("input", () => this.applyFilters());
          element.addEventListener("change", () => this.applyFilters());
        }
      }
    );

    // Sorting
    const sortField = this.container.querySelector("#sort-field");
    const sortDirection = this.container.querySelector("#sort-direction");

    if (sortField) {
      sortField.addEventListener("change", () => this.applySort());
      const sortOptions = Array.from(sortField.querySelectorAll("option")).map(
        (option) => {
          return "col-" + option.value.replace("_", "-");
        }
      );
      const sortCols = this.container.querySelectorAll("th");
      sortCols.forEach((col) => {
        if (sortOptions.includes(col.id)) {
          col.setAttribute("data-bs-toggle", "tooltip");
          col.setAttribute(
            "data-bs-title",
            `Click to sort by ${col.innerText}`
          );
          col.addEventListener("click", () => {
            this.toggleSortDirection();
            this.applySort(col.id.replace("col-", ""));
          });
        }
      });
    }
    if (sortDirection) {
      this.toggleSortDirection();
      sortDirection.addEventListener("click", (e) => {
        this.toggleSortDirection();
        this.applySort();
      });
    }
  }

  updateSortIcon(button, direction) {
    // Clear existing content
    button.innerHTML = "";

    // Create new icon
    const icon = document.createElement("i");
    icon.className = `fas fa-sort-amount-${
      direction === "asc" ? "up" : "down"
    }`;
    button.appendChild(icon);
  }

  parseDateValue(dateStr) {
    if (!dateStr) return null;

    // Handle different date formats
    let date;
    if (dateStr.includes("T")) {
      // ISO format
      date = new Date(dateStr);
    } else {
      // Try different formats
      const formats = [
        "DD/MM/YYYY HH:mm",
        "DD/MM/YYYY hh:mm A",
        "YYYY-MM-DD HH:mm:ss",
        "YYYY-MM-DD HH:mm",
        "YYYY-MM-DD",
      ];

      for (const format of formats) {
        try {
          // Parse the date string
          let dateDayjs = dayjs(dateStr, formats);
          // Convert to JavaScript Date object if needed
          date = dateDayjs.toDate();
          if (!isNaN(date)) break;
        } catch (e) {
          continue;
        }
      }
    }

    return isNaN(date) ? null : date;
  }

  applyFilters() {
    const searchTerm = this.container
      .querySelector("#search-input")
      ?.value.toLowerCase();
    const statusFilter = this.container.querySelector("#status-filter")?.value;
    const priorityFilter =
      this.container.querySelector("#priority-filter")?.value;
    const dateFilter = this.container.querySelector("#date-filter")?.value;

    const selectedTagIds = Array.from(
      this.container.querySelectorAll(".tag-filter-checkbox:checked")
    ).map((cb) => cb.value);

    const rows = this.container.querySelectorAll(
      "tbody tr:not([id='no-results'])"
    );
    let totalHideCount = 0;

    rows.forEach((row) => {
      let show = true;

      // Text search
      if (searchTerm) {
        const textContent = row.textContent.toLowerCase();
        show = show && textContent.includes(searchTerm);
      }

      // Status filter
      if (statusFilter) {
        const status = row
          .querySelector('[data-field="status"]')
          ?.textContent.trim();
        show = show && status === statusFilter;
      }

      // Priority filter
      if (priorityFilter) {
        const priority = row
          .querySelector('[data-field="priority"]')
          ?.textContent.trim();
        show = show && priority === priorityFilter;
      }

      // Date filter
      if (dateFilter) {
        const dueDateCell =
          row.querySelector('[data-field="due_date"]') ||
          row.querySelector('[data-field="due-date"]');
        if (dueDateCell) {
          const dueDate = this.parseDateValue(dueDateCell.textContent.trim());
          const filterDate = this.parseDateValue(dateFilter);
          if (dueDate && filterDate) {
            show =
              show &&
              dueDate.toLocaleDateString() === filterDate.toLocaleDateString();
          }
        }
      }

      // Tag filtering
      if (selectedTagIds.length > 0) {
        const tagElements = row.querySelectorAll('[data-field="tags"] .badge');
        const rowTagIds = Array.from(tagElements).map(
          (tag) => tag.dataset.tagId // Make sure your tags have data-tag-id attribute
        );

        // Show row only if it has at least one selected tag
        show = show && selectedTagIds.some((id) => rowTagIds.includes(id));
      }

      if (!show) {
        totalHideCount++;
      }

      row.style.display = show ? "" : "none";
    });

    const noResults = this.container.querySelector("#no-results");
    if (totalHideCount === rows.length) {
      noResults.classList.remove("d-none");
    } else {
      noResults.classList.add("d-none");
    }

    this.savePreferences();
  }

  applySort(fieldName) {
    const sortField = this.container.querySelector("#sort-field");
    const sortDirection = this.container.querySelector("#sort-direction");

    if (!sortField || !sortDirection) return;

    if (fieldName) {
      const sortOptions = sortField.querySelectorAll("option");

      sortOptions.forEach((option) => {
        if (option.value.replace(/_/g, "-") === fieldName) {
          option.selected = true;
        }
      });
    }

    const field = fieldName || sortField.value;
    const direction = sortDirection.dataset.direction || "asc";

    const tbody = this.container.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    rows.sort((a, b) => {
      const aValElement =
        a.querySelector(`[data-field="${field.replace(/_/g, "-")}"]`) ||
        a.querySelector(`[data-field="${field.replace(/-/g, "_")}"]`);
      const bValElement =
        b.querySelector(`[data-field="${field.replace(/_/g, "-")}"]`) ||
        b.querySelector(`[data-field="${field.replace(/-/g, "_")}"]`);
      let aVal = aValElement?.textContent.trim();
      let bVal = bValElement?.textContent.trim();

      // Handle priority sorting
      if (field === "priority") {
        const priorityOrder = { High: 3, Medium: 2, Low: 1 };
        aVal = priorityOrder[aVal] || 0;
        bVal = priorityOrder[bVal] || 0;
      }
      // Handle status sorting
      else if (field === "status") {
        const statusOrder = { Pending: 1, "In Progress": 2, Completed: 3 };
        aVal = statusOrder[aVal] || 0;
        bVal = statusOrder[bVal] || 0;
      } else {
        // Handle date sorting
        aVal = this.parseDateValue(aVal);
        bVal = this.parseDateValue(bVal);

        // Handle null dates
        if (!aVal && !bVal) return 0;
        if (!aVal) return direction === "asc" ? -1 : 1;
        if (!bVal) return direction === "asc" ? 1 : -1;

        return direction === "asc"
          ? aVal.getTime() - bVal.getTime()
          : bVal.getTime() - aVal.getTime();
      }

      if (aVal < bVal) return direction === "asc" ? -1 : 1;
      if (aVal > bVal) return direction === "asc" ? 1 : -1;
      return 0;
    });

    // Clear and re-append sorted rows
    tbody.innerHTML = "";
    rows.forEach((row) => tbody.appendChild(row));

    this.savePreferences();
  }

  loadSavedPreferences() {
    const preferences = JSON.parse(
      localStorage.getItem(this.settingKey) || "{}"
    );

    // Apply saved sort field
    if (preferences.sortField) {
      const sortField = this.container.querySelector("#sort-field");
      if (sortField) {
        sortField.value = preferences.sortField;
      }
    }

    // Apply saved sort direction
    if (preferences.sortDirection) {
      const sortDirection = this.container.querySelector("#sort-direction");
      if (sortDirection) {
        let loadedDirection =
          preferences.sortDirection === "asc" ? "up" : "down";
        sortDirection.dataset.direction = preferences.sortDirection;
        sortDirection.innerHTML = `<i class="fas fa-sort-amount-${loadedDirection}"></i>`;
      }
    }

    // Apply saved filters
    if (preferences.filters) {
      const { searchTerm, status, priority, date } = preferences.filters;

      const searchInput = this.container.querySelector("#search-input");
      const statusFilter = this.container.querySelector("#status-filter");
      const priorityFilter = this.container.querySelector("#priority-filter");
      const dateFilter = this.container.querySelector("#date-filter");

      if (searchInput && searchTerm) searchInput.value = searchTerm;
      if (statusFilter && status) statusFilter.value = status;
      if (priorityFilter && priority) priorityFilter.value = priority;
      if (dateFilter && date) dateFilter.value = date;

      // Load tag filters
      if (preferences.tagFilters) {
        preferences.tagFilters.forEach((tagId) => {
          const checkbox = this.container.querySelector(
            `.tag-filter-checkbox[value="${tagId}"]`
          );
          if (checkbox) {
            checkbox.checked = true;
          }
        });
        this.updateTagFilterIndicator();
      }

      this.applyFilters();
    }

    this.applySort();
  }

  savePreferences() {
    const preferences = {
      sortField: this.container.querySelector("#sort-field")?.value,
      sortDirection:
        this.container.querySelector("#sort-direction")?.dataset.direction,
      filters: {
        searchTerm: this.container.querySelector("#search-input")?.value,
        status: this.container.querySelector("#status-filter")?.value,
        priority: this.container.querySelector("#priority-filter")?.value,
        date: this.container.querySelector("#date-filter")?.value,
      },
      tagFilters: Array.from(
        this.container.querySelectorAll(".tag-filter-checkbox:checked")
      ).map((cb) => cb.value),
    };

    localStorage.setItem(this.settingKey, JSON.stringify(preferences));
  }
}

// Initialize table
document.addEventListener("DOMContentLoaded", () => {
  const taskTable = document.querySelector("#task-table");
  if (taskTable && taskTable.querySelector("#table-toolbar")) {
    new TaskTable(taskTable);
  }

  // const logoutButton = document.querySelector("#logout");
  // if (logoutButton) {
  //   logoutButton.addEventListener("click", (e) => {
  //     TaskTable.clearSettings();
  //   });
  // }
});
