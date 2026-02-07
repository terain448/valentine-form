let selectedFiles = [];
const limits = {
  basic: 10,
  plus: 25,
  premium: 50
};

const packageLimits = {
  basic: 10,
  plus: 25,
  premium: 50
};

const form = document.getElementById("orderForm");
const errorBox = document.getElementById("errorBox");
const packageSelect = document.querySelector("select[name='package']");
const photoInput = document.getElementById("photos");
const photoHint = document.getElementById("photoHint");
const previewArea = document.getElementById("photoPreview");
const fileLabel = document.querySelector(".file-label");

const passwordChoice = document.getElementById("passwordChoice");
const passwordArea = document.getElementById("passwordArea");
const passwordInput = document.getElementById("sitePassword");
const togglePassword = document.getElementById("togglePassword");

const musicChoice = document.getElementById("musicChoice");
const musicArea = document.getElementById("musicArea");

musicChoice.addEventListener("change", () => {
  if (musicChoice.value === "yes") {
    musicArea.classList.remove("hidden");
    document
      .getElementById("music_detail")
      .setAttribute("data-required", "true");
  } else {
    musicArea.classList.add("hidden");
    const musicDetail = document.getElementById("music_detail");
    musicDetail.removeAttribute("data-required");
    musicDetail.value = "";
  }
});


/* Şifre alanını aç/kapat */
passwordChoice.addEventListener("change", () => {
  const isYes = passwordChoice.value === "yes";

  // Alanı aç / kapat
  passwordArea.classList.toggle("hidden", !isYes);

  if (isYes) {
    // EVET → şifre zorunlu
    passwordInput.setAttribute("data-required", "true");
  } else {
    // HAYIR → temizle
    passwordInput.removeAttribute("data-required");
    passwordInput.value = "";
  }
});

/* Şifre göster / gizle */
if (togglePassword && passwordInput) {
  togglePassword.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";
    passwordInput.type = isHidden ? "text" : "password";
    togglePassword.classList.toggle("visible", isHidden);
  });
}

/* Paket → fotoğraf limiti */
packageSelect.addEventListener("change", () => {
  const max = limits[packageSelect.value];

  photoHint.textContent = max
    ? `Maksimum ${max} fotoğraf yükleyebilirsiniz.`
    : "";

  if (selectedFiles.length > max) {
    selectedFiles = selectedFiles.slice(0, max);
    syncFileInput();
    renderPreview();
  }
});

packageSelect.addEventListener("change", () => {
  const pkg = packageSelect.value;

  const passwordLabel = document.querySelector(
    'label[for="passwordChoice"]'
  );

  if (pkg === "basic") {
    // BASIC → şifre sorusu tamamen yok
    passwordLabel.classList.add("hidden");
    passwordChoice.classList.add("hidden");
    passwordArea.classList.add("hidden");

    passwordChoice.value = "";
    passwordInput.value = "";

    passwordChoice.removeAttribute("data-required");
    passwordInput.removeAttribute("data-required");
  } else {
    // PLUS / PREMIUM → şifre sorusu var ve zorunlu
    passwordLabel.classList.remove("hidden");
    passwordChoice.classList.remove("hidden");

    passwordChoice.setAttribute("data-required", "true");
  }
});

/* File label + preview */
photoInput.addEventListener("change", () => {
  const newFiles = Array.from(photoInput.files);
  const max = limits[packageSelect.value] || Infinity;

  newFiles.forEach(file => {
    if (
      file.type.startsWith("image/") &&
      selectedFiles.length < max
    ) {
      selectedFiles.push(file);
    }
  });

  syncFileInput();
  renderPreview();
});


/* Form submit */
form.addEventListener("submit", (e) => {
  errorBox.innerHTML = "";
  let errors = [];

    document.querySelectorAll("[data-required]").forEach((el) => {
        if (!el.value.trim()) {
            const label = document.querySelector(`label[for="${el.id}"]`);
            const labelText = label ? label.textContent : "Bu alan";

            errors.push(`"${labelText}" alanı boş bırakılamaz`);
        }
    });


  const limits = PACKAGE_LIMITS;
  const selectedPackage = packageSelect.value;

  if (photoInput.files.length > limits[selectedPackage]) {
    errors.push(
      `Seçilen paket için maksimum ${limits[selectedPackage]} fotoğraf yükleyebilirsiniz`
    );
  }

  if (errors.length) {
    e.preventDefault();
    errorBox.innerHTML = errors.join("<br>");
  }
});

/* Dark / Light toggle */
const toggle = document.getElementById("themeToggle");
const body = document.body;

if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark");
  toggle.classList.add("dark");
}

toggle.addEventListener("click", () => {
  const isDark = body.classList.toggle("dark");
  toggle.classList.toggle("dark", isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
});

function syncFileInput() {
  const dataTransfer = new DataTransfer();

  selectedFiles.forEach(file => {
    dataTransfer.items.add(file);
  });

  photoInput.files = dataTransfer.files;
}

function renderPreview() {
  previewArea.innerHTML = "";

  if (!selectedFiles.length) {
    previewArea.classList.add("hidden");
    return;
  }

  previewArea.classList.remove("hidden");

  selectedFiles.forEach((file, index) => {
    const reader = new FileReader();

    reader.onload = e => {
      const card = document.createElement("div");
      card.className = "photo-card";

      const img = document.createElement("img");
      img.src = e.target.result;

      const removeBtn = document.createElement("button");
      removeBtn.className = "remove-photo";
      removeBtn.innerHTML = "×";

      removeBtn.addEventListener("click", () => {
        selectedFiles.splice(index, 1);
        syncFileInput();
        renderPreview();
      });

      card.appendChild(img);
      card.appendChild(removeBtn);
      previewArea.appendChild(card);
    };

    reader.readAsDataURL(file);
  });
}

