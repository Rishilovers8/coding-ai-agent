/* Ramify RR - Frontend Logic */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("translateForm");
  const dropZone = document.getElementById("dropZone");
  const videoInput = document.getElementById("videoInput");
  const fileInfo = document.getElementById("fileInfo");
  const fileName = document.getElementById("fileName");
  const fileSize = document.getElementById("fileSize");
  const removeFile = document.getElementById("removeFile");
  const submitBtn = document.getElementById("submitBtn");
  const useElevenlabs = document.getElementById("useElevenlabs");
  const voiceIdGroup = document.getElementById("voiceIdGroup");
  const progressSection = document.getElementById("progressSection");
  const progressBar = document.getElementById("progressBar");
  const progressSteps = document.getElementById("progressSteps");
  const errorMsg = document.getElementById("errorMsg");
  const resultsSection = document.getElementById("resultsSection");

  /* File selection */
  videoInput.addEventListener("change", () => {
    if (videoInput.files.length > 0) showFileInfo(videoInput.files[0]);
  });

  /* Drag and drop */
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      videoInput.files = e.dataTransfer.files;
      showFileInfo(e.dataTransfer.files[0]);
    }
  });

  removeFile.addEventListener("click", () => {
    videoInput.value = "";
    fileInfo.classList.remove("show");
    submitBtn.disabled = true;
  });

  useElevenlabs.addEventListener("change", () => {
    voiceIdGroup.classList.toggle("show", useElevenlabs.checked);
  });

  function showFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.classList.add("show");
    submitBtn.disabled = false;
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  }

  /* Form submission */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!videoInput.files.length) return;

    // Reset UI
    errorMsg.classList.remove("show");
    resultsSection.classList.remove("show");
    progressSection.classList.add("show");
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";
    resetProgress();

    const formData = new FormData();
    formData.append("video", videoInput.files[0]);
    formData.append("target_lang", document.getElementById("targetLang").value);
    formData.append("use_elevenlabs", useElevenlabs.checked ? "true" : "false");
    formData.append(
      "voice_id",
      document.getElementById("voiceId").value || ""
    );

    // Simulate progress steps while waiting
    simulateProgress();

    try {
      const response = await fetch("/translate", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        showError(data.error || "An unexpected error occurred.");
        return;
      }

      // Show results
      completeProgress();
      document.getElementById("srcLangName").textContent = data.source_lang;
      document.getElementById("tgtLangName").textContent = data.target_lang;
      document.getElementById("transcriptionText").textContent =
        data.transcription;
      document.getElementById("translationText").textContent =
        data.translation;
      document.getElementById("downloadBtn").href = data.download_url;
      resultsSection.classList.add("show");
    } catch (err) {
      showError("Network error: " + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Translate Video";
    }
  });

  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.add("show");
    progressSection.classList.remove("show");
  }

  function resetProgress() {
    progressBar.style.width = "0%";
    progressSteps.querySelectorAll("li").forEach((li) => {
      li.classList.remove("active", "done");
      li.querySelector(".step-icon").textContent = "○";
    });
  }

  function simulateProgress() {
    const steps = progressSteps.querySelectorAll("li");
    let current = 0;
    const interval = setInterval(() => {
      if (current >= 5) {
        clearInterval(interval);
        return;
      }
      if (current > 0) {
        steps[current - 1].classList.remove("active");
        steps[current - 1].classList.add("done");
        steps[current - 1].querySelector(".step-icon").textContent = "●";
      }
      steps[current].classList.add("active");
      steps[current].querySelector(".step-icon").innerHTML =
        '<span class="spinner"></span>';
      progressBar.style.width = ((current + 1) / 6) * 100 + "%";
      current++;
    }, 3000);
    window._progressInterval = interval;
  }

  function completeProgress() {
    clearInterval(window._progressInterval);
    progressBar.style.width = "100%";
    progressSteps.querySelectorAll("li").forEach((li) => {
      li.classList.remove("active");
      li.classList.add("done");
      li.querySelector(".step-icon").textContent = "●";
    });
  }
});
