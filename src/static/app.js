document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const authForm = document.getElementById("auth-form");
  const authModeToggle = document.getElementById("toggle-auth-mode");
  const authButton = document.getElementById("auth-button");
  const authEmailInput = document.getElementById("auth-email");
  const authPasswordInput = document.getElementById("auth-password");
  const userInfo = document.getElementById("user-info");
  const adminContainer = document.getElementById("admin-container");
  const createActivityForm = document.getElementById("create-activity-form");
  const activityNameInput = document.getElementById("activity-name");
  const activityDescriptionInput = document.getElementById("activity-description");
  const activityScheduleInput = document.getElementById("activity-schedule");
  const activityMaxInput = document.getElementById("activity-max");
  const editActivityForm = document.getElementById("edit-activity-form");
  const editActivityNameInput = document.getElementById("edit-activity-name");
  const editActivityDescriptionInput = document.getElementById("edit-activity-description");
  const editActivityScheduleInput = document.getElementById("edit-activity-schedule");
  const editActivityMaxInput = document.getElementById("edit-activity-max");
  const cancelEditButton = document.getElementById("cancel-edit");

  let authMode = "login";
  let currentUserRole = null;
  let currentUserEmail = null;
  let currentActivities = {};
  let editingActivity = null;

  function getAuthToken() {
    return localStorage.getItem("activityAuthToken");
  }

  function setAuthToken(token) {
    localStorage.setItem("activityAuthToken", token);
  }

  function clearAuthToken() {
    localStorage.removeItem("activityAuthToken");
  }

  function getAuthHeaders() {
    const token = getAuthToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function showMessage(text, type = "success") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function updateCurrentUser() {
    const token = getAuthToken();
    if (!token) {
      userInfo.classList.add("hidden");
      adminContainer.classList.add("hidden");
      return;
    }

    try {
      const response = await fetch("/auth/me", {
        headers: getAuthHeaders(),
      });
      if (!response.ok) {
        throw new Error("Not authenticated");
      }
      const user = await response.json();
      currentUserRole = user.role;
      currentUserEmail = user.email;
      userInfo.textContent = `Logged in as ${user.email} (${user.role})`;
      userInfo.classList.remove("hidden");
      if (user.role === "admin" || user.role === "organizer") {
        adminContainer.classList.remove("hidden");
      } else {
        adminContainer.classList.add("hidden");
      }
    } catch (error) {
      clearAuthToken();
      userInfo.classList.add("hidden");
      adminContainer.classList.add("hidden");
      currentUserRole = null;
      currentUserEmail = null;
      console.error("Auth session invalid:", error);
    }
  }

  function toggleAuthMode() {
    authMode = authMode === "login" ? "register" : "login";
    authButton.textContent = authMode === "login" ? "Login" : "Register";
    authModeToggle.textContent = authMode === "login" ? "Switch to Register" : "Switch to Login";
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = `
        <option value="">-- Select an activity --</option>
      `;

      currentActivities = activities;
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const attendedCount = details.attended_count || 0;
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        const isSignedUp = currentUserEmail && details.participants.includes(currentUserEmail);
        const checkinButton = currentUserRole === "student" && isSignedUp ? `<button class="checkin-btn" data-activity="${name}">Check In</button>` : "";
        const viewAttendanceButton = isManager ? `<button class="view-attendance-btn" data-activity="${name}">View Attendance (${attendedCount})</button>` : "";

        const adminControls = isManager
          ? `
            <div class="activity-admin-controls">
              <button class="edit-activity" data-activity="${name}">Edit</button>
              <button class="delete-activity" data-activity="${name}">Delete</button>
              ${viewAttendanceButton}
            </div>
          `
          : "";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
          ${checkinButton}
          ${adminControls}
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
      document.querySelectorAll(".delete-activity").forEach((button) => {
        button.addEventListener("click", () => handleDeleteActivity(button.getAttribute("data-activity")));
      });
      document.querySelectorAll(".edit-activity").forEach((button) => {
        button.addEventListener("click", () => handleEditActivity(button.getAttribute("data-activity")));
      });
      document.querySelectorAll(".checkin-btn").forEach((button) => {
        button.addEventListener("click", () => handleCheckin(button.getAttribute("data-activity")));
      });
      document.querySelectorAll(".view-attendance-btn").forEach((button) => {
        button.addEventListener("click", () => handleViewAttendance(button.getAttribute("data-activity")));
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    event.preventDefault();
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const token = getAuthToken();

    if (!token) {
      showMessage("You must be logged in to unregister.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister`,
        {
          method: "DELETE",
          headers: {
            ...getAuthHeaders(),
          },
        }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  async function handleCheckin(activity) {
    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}/checkin`, {
        method: "POST",
        headers: {
          ...getAuthHeaders(),
        },
      });
      const result = await response.json();
      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "Failed to check in", "error");
      }
    } catch (error) {
      showMessage("Failed to check in. Please try again.", "error");
      console.error("Checkin error:", error);
    }
  }

  async function handleViewAttendance(activity) {
    try {
      const response = await fetch(`/activities/${encodeURIComponent(activity)}/attendance`, {
        headers: {
          ...getAuthHeaders(),
        },
      });
      const result = await response.json();
      if (response.ok) {
        const attendedList = result.attended.length > 0 ? result.attended.join(", ") : "No one has checked in yet.";
        showMessage(`Attendance for ${activity}: ${attendedList} (${result.count} total)`, "info");
      } else {
        showMessage(result.detail || "Failed to fetch attendance", "error");
      }
    } catch (error) {
      showMessage("Failed to fetch attendance. Please try again.", "error");
      console.error("View attendance error:", error);
    }
  }

  function handleEditActivity(activity) {
    const activityData = currentActivities[activity];
    if (!activityData) {
      showMessage("Unable to load activity details for editing.", "error");
      return;
    }

    editingActivity = activity;
    editActivityNameInput.value = activity;
    editActivityDescriptionInput.value = activityData.description;
    editActivityScheduleInput.value = activityData.schedule;
    editActivityMaxInput.value = activityData.max_participants;
    editActivityForm.classList.remove("hidden");
    window.scrollTo({ top: editActivityForm.offsetTop - 20, behavior: "smooth" });
  }

  editActivityForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!editingActivity) {
      showMessage("No activity selected for editing.", "error");
      return;
    }

    const description = editActivityDescriptionInput.value.trim();
    const schedule = editActivityScheduleInput.value.trim();
    const maxParticipants = Number(editActivityMaxInput.value);

    if (!description || !schedule || maxParticipants <= 0) {
      showMessage("Please fill all fields for the activity.", "error");
      return;
    }

    try {
      const response = await fetch(`/activities/${encodeURIComponent(editingActivity)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          description,
          schedule,
          max_participants: maxParticipants,
        }),
      });
      const result = await response.json();
      if (response.ok) {
        showMessage(result.message, "success");
        editActivityForm.classList.add("hidden");
        editingActivity = null;
        fetchActivities();
      } else {
        showMessage(result.detail || "Failed to update activity", "error");
      }
    } catch (error) {
      showMessage("Failed to update activity. Please try again.", "error");
      console.error("Edit activity error:", error);
    }
  });

  cancelEditButton.addEventListener("click", () => {
    editActivityForm.classList.add("hidden");
    editingActivity = null;
  });

  createActivityForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = activityNameInput.value.trim();
    const description = activityDescriptionInput.value.trim();
    const schedule = activityScheduleInput.value.trim();
    const maxParticipants = Number(activityMaxInput.value);

    if (!name || !description || !schedule || maxParticipants <= 0) {
      showMessage("Please fill in all activity fields.", "error");
      return;
    }

    try {
      const response = await fetch("/activities", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          name,
          description,
          schedule,
          max_participants: maxParticipants,
        }),
      });
      const result = await response.json();
      if (response.ok) {
        showMessage(result.message, "success");
        createActivityForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "Failed to create activity", "error");
      }
    } catch (error) {
      showMessage("Failed to create activity. Please try again.", "error");
      console.error("Create activity error:", error);
    }
  });

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const activity = document.getElementById("activity").value;
    const token = getAuthToken();

    if (!token) {
      showMessage("Please log in before signing up for an activity.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
          headers: {
            ...getAuthHeaders(),
          },
        }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = authEmailInput.value;
    const password = authPasswordInput.value;

    const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";
    const payload = { email, password };

    if (authMode === "register") {
      payload.role = "student";
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();

      if (response.ok) {
        setAuthToken(result.token);
        showMessage(result.message, "success");
        authPasswordInput.value = "";
        updateCurrentUser();
        fetchActivities();
      } else {
        showMessage(result.detail || "Authentication failed", "error");
      }
    } catch (error) {
      showMessage("Authentication request failed. Please try again.", "error");
      console.error("Auth error:", error);
    }
  });

  authModeToggle.addEventListener("click", () => {
    toggleAuthMode();
  });

  updateCurrentUser();
  fetchActivities();
});
