async function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    const statusDiv = document.getElementById('uploadStatus');
    const questionInput = document.getElementById('questionInput'); // Get the input element

    if (!file) {
        statusDiv.textContent = "Please select a PDF file.";
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Server Error:", response.status, errorText);
            statusDiv.textContent = `Upload failed: ${response.status} - ${errorText}`;
            return; // Stop here if the upload fails
        }

        const data = await response.json();
        statusDiv.textContent = data.message;

        // Enable the question input ONLY if the upload is successful
        questionInput.disabled = false;  // Enable it
        questionInput.placeholder = "Ask a question about " + file.name; // Optional: Set a helpful placeholder

    } catch (error) {
        console.error("Fetch Error:", error);
        statusDiv.textContent = "Upload failed: " + error;
    }
}


async function askQuestion() {
    const pdfName = document.getElementById('pdfFile').files[0].name; // Get the PDF name
    const question = document.getElementById('questionInput').value;
    const answerOutput = document.getElementById('answerOutput');

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pdf_name: pdfName, question: question })
        });

        const data = await response.json();
        answerOutput.textContent = data.answer;
    } catch (error) {
        answerOutput.textContent = "Error asking question.";
        console.error(error);
    }
}

// Disable the question input initially
document.getElementById('questionInput').disabled = true;