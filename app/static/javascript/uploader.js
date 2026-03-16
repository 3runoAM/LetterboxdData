const sendButton = document.getElementById("sendButton");
const fileInput = document.getElementById("inputFile");
const form = document.getElementById("uploadForm");

sendButton.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) form.submit();
})

/*--------------------------------------------------------------------------------------------------------------------*/

document.addEventListener("DOMContentLoaded", () => {
    const feedbackContainer = document.getElementById("feedbackContainer");

    if (feedbackContainer) {
        setTimeout(() => {
            feedbackContainer.remove();
        }, 2000);
    }
});