const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");
const fileCount = document.getElementById("file-count");
const toolSelect = document.getElementById("tool");

// Update file list when files are selected
fileInput.addEventListener("change", () => {
    fileList.innerHTML = "";
    const files = Array.from(fileInput.files);

    fileCount.textContent = files.length > 0
        ? `${files.length} file${files.length > 1 ? 's' : ''} selected`
        : '';

    files.forEach(file => {
        const div = document.createElement("div");
        div.className = "file-item";
        div.textContent = file.name;
        fileList.appendChild(div);
    });
});

// Validate before form submission
function handleFormSubmit() {
    const tool = toolSelect.value;
    const files = fileInput.files;

    if (!tool) {
        alert("Please select a tool.");
        return false;
    }

    if (!files.length) {
        alert("Please select at least one file.");
        return false;
    }

    return true;
}