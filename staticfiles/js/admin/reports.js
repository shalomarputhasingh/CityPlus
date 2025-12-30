const photoInput = document.getElementById("photo");
const preview = document.getElementById("preview");
const submitBtn = document.getElementById("submitBtn");

photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (file) {
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
  }
});

submitBtn.addEventListener("click", () => {
  const desc = document.getElementById("description").value.trim();
  const type = document.getElementById("issueType").value;

  if (!desc || !type) {
    alert("Please fill issue description and issue type");
    return;
  }

  alert("✅ Issue submitted successfully (client-side)");
  
  // reset
  document.getElementById("description").value = "";
  document.getElementById("issueType").value = "";
  preview.style.display = "none";
});
