import { supabase } from "../supabase.js";

const submitBtn = document.getElementById("submitBtn");
const photoInput = document.getElementById("photo");

submitBtn.addEventListener("click", async () => {
  const citizen_id = localStorage.getItem("citizen_id");
  const desc = description.value.trim();
  const type = issueType.value;
  const block = document.getElementById("block").value;
  const village = document.getElementById("village").value;
  const landmark = document.getElementById("landmark").value;
  const location = document.getElementById("location").value;
  const file = photoInput.files[0];

  if (!desc || !type || !file) {
    alert("Fill required fields + upload photo");
    return;
  }

  // upload photo
  const fileName = `${Date.now()}_${file.name}`;
  const { data: uploadData, error: uploadError } =
    await supabase.storage
      .from("issues-photos")
      .upload(fileName, file);

  if (uploadError) {
    alert("Photo upload failed");
    return;
  }

  const photo_url =
    supabase.storage
      .from("issues-photos")
      .getPublicUrl(fileName).data.publicUrl;

  // insert issue
  const { error } = await supabase.from("issues").insert({
    citizen_id,
    description: desc,
    issue_type: type,
    block,
    village,
    landmark,
    location,
    photo_url
  });

  if (error) {
    alert("Issue submit failed");
    return;
  }

  alert("✅ Issue submitted successfully");
});
