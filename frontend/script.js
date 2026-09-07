// =====================================
// ResolveAI
// Frontend Logic
// =====================================


// =====================================
// State
// =====================================

let selectedDocument = null;

let isUploading = false;

let isAsking = false;


// =====================================
// Elements
// =====================================

const fileInput =
    document.getElementById("fileInput");

const fileName =
    document.getElementById("fileName");

const uploadStatus =
    document.getElementById("uploadStatus");

const selectedDocumentElement =
    document.getElementById("selectedDocument");

const questionInput =
    document.getElementById("questionInput");

const askButton =
    document.getElementById("askButton");

const answerElement =
    document.getElementById("answer");


// =====================================
// File Selection
// =====================================

fileInput.addEventListener(
    "change",
    async function () {

        // Get selected file
        const file =
            fileInput.files[0];


        // Nothing selected
        if (!file) {
            return;
        }


        // Prevent duplicate upload
        if (isUploading) {
            return;
        }


        // Check PDF
        if (
            !file.name
                .toLowerCase()
                .endsWith(".pdf")
        ) {

            fileName.textContent =
                "Please select a PDF file.";

            uploadStatus.textContent =
                "";

            return;
        }


        // =====================================
        // Reset state
        // =====================================

        selectedDocument = null;


        questionInput.disabled = true;

        askButton.disabled = true;


        // =====================================
        // Update UI
        // =====================================

        fileName.textContent =
            `Selected: ${file.name}`;


        selectedDocumentElement.textContent =
            "Processing document...";


        uploadStatus.textContent =
            "Uploading and processing document...";


        answerElement.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ✦
                </div>

                <h4>
                    Processing document...
                </h4>

                <p>
                    Reading and indexing your PDF.
                </p>

            </div>

        `;


        // =====================================
        // Upload
        // =====================================

        await uploadDocument(file);

    }
);


// =====================================
// Upload Document
// =====================================

async function uploadDocument(file) {

    // Lock upload
    isUploading = true;

    fileInput.disabled = true;


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        console.log(
            "Uploading:",
            file.name
        );


        // =====================================
        // Send request
        // =====================================

        const response =
            await fetch(
                "/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        console.log(
            "Upload status:",
            response.status
        );


        // =====================================
        // Read response safely
        // =====================================

        const responseText =
            await response.text();


        console.log(
            "Upload response:",
            responseText
        );


        // Empty response
        if (!responseText.trim()) {

            throw new Error(
                "Server returned an empty response."
            );

        }


        // =====================================
        // Parse JSON
        // =====================================

        let data;


        try {

            data =
                JSON.parse(responseText);

        }

        catch (error) {

            console.error(
                "Invalid JSON:",
                responseText
            );


            throw new Error(
                "Server returned an invalid response."
            );

        }


        // =====================================
        // Backend error
        // =====================================

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Upload failed."
            );

        }


        // =====================================
        // Successful upload
        // =====================================

        selectedDocument =
            data.document ||
            file.name;


        fileName.textContent =
            `Selected: ${selectedDocument}`;


        selectedDocumentElement.textContent =
            selectedDocument;


        uploadStatus.textContent =
            `✓ Document ready • ${data.chunks_indexed} chunks indexed`;


        // Enable question area
        questionInput.disabled = false;

        askButton.disabled = false;


        // Reset answer
        answerElement.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ✦
                </div>

                <h4>
                    Document ready
                </h4>

                <p>
                    Ask a question about
                    ${escapeHtml(selectedDocument)}
                </p>

            </div>

        `;


        // Focus question
        questionInput.focus();


        console.log(
            "Document ready:",
            selectedDocument
        );

    }


    catch (error) {

        console.error(
            "Upload error:",
            error
        );


        // Reset state
        selectedDocument = null;


        selectedDocumentElement.textContent =
            "No document selected";


        questionInput.disabled = true;

        askButton.disabled = true;


        uploadStatus.textContent =
            `Upload failed: ${error.message}`;


        answerElement.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    !
                </div>

                <h4>
                    Upload failed
                </h4>

                <p>
                    ${escapeHtml(error.message)}
                </p>

            </div>

        `;

    }


    finally {

        // Unlock upload
        isUploading = false;

        fileInput.disabled = false;

    }

}


// =====================================
// Ask Question
// =====================================

async function askQuestion() {

    // Prevent multiple questions
    if (isAsking) {
        return;
    }


    const question =
        questionInput.value.trim();


    // No document
    if (!selectedDocument) {

        showMessage(
            "No document selected",
            "Please upload a PDF first."
        );

        return;
    }


    // Empty question
    if (!question) {
        return;
    }


    isAsking = true;


    // =====================================
    // Loading UI
    // =====================================

    askButton.disabled = true;


    askButton.innerHTML = `
        Thinking...
        <span>✦</span>
    `;


    answerElement.innerHTML = `

        <div class="empty-state">

            <div class="empty-icon">
                ✦
            </div>

            <h4>
                Thinking...
            </h4>

            <p>
                Finding the answer in your document.
            </p>

        </div>

    `;


    try {

        // =====================================
        // Ask backend
        // =====================================

        const response =
            await fetch(
                "/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        document_name:
                            selectedDocument

                    })
                }
            );


        // Read response
        const responseText =
            await response.text();


        if (!responseText.trim()) {

            throw new Error(
                "Server returned an empty response."
            );

        }


        let data;


        try {

            data =
                JSON.parse(responseText);

        }

        catch (error) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        // Backend error
        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to get answer."
            );

        }


        // =====================================
        // Display answer
        // =====================================

        displayAnswer(
            data.answer
        );

    }


    catch (error) {

        console.error(
            "Question error:",
            error
        );


        showMessage(
            "Something went wrong",
            error.message
        );

    }


    finally {

        isAsking = false;


        askButton.disabled = false;


        askButton.innerHTML = `
            Send
            <span>↵</span>
        `;

    }

}


// =====================================
// Send Button
// =====================================

askButton.addEventListener(
    "click",
    askQuestion
);


// =====================================
// Enter = Send
// Shift + Enter = New Line
// =====================================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();

        }

    }
);


// =====================================
// Display Answer
// =====================================

function displayAnswer(text) {

    if (!text) {

        showMessage(
            "No answer",
            "The AI did not return an answer."
        );

        return;
    }


    answerElement.innerHTML = `

        <div class="generated-answer">

            ${formatAnswer(text)}

        </div>

    `;

}


// =====================================
// Format Answer
// =====================================

function formatAnswer(text) {

    let answer =
        text
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .trim();


    // Escape HTML
    answer =
        escapeHtml(answer);


    // Bold
    answer =
        answer.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    // Headings
    answer =
        answer.replace(
            /^### (.+)$/gm,
            "<h4>$1</h4>"
        );


    answer =
        answer.replace(
            /^## (.+)$/gm,
            "<h4>$1</h4>"
        );


    // Bullets
    answer =
        answer.replace(
            /^[\*\-]\s+(.+)$/gm,
            "<li>$1</li>"
        );


    // Numbered lists
    answer =
        answer.replace(
            /^\d+\.\s+(.+)$/gm,
            "<li>$1</li>"
        );


    // Wrap lists
    answer =
        answer.replace(
            /(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/gs,
            "<ul>$1</ul>"
        );


    // Paragraphs
    const lines =
        answer.split("\n");


    let result = "";


    for (const line of lines) {

        const cleanLine =
            line.trim();


        if (!cleanLine) {
            continue;
        }


        if (
            cleanLine.startsWith("<h4>") ||
            cleanLine.startsWith("<ul>")
        ) {

            result +=
                cleanLine;

        }

        else {

            result +=
                `<p>${cleanLine}</p>`;

        }

    }


    return result;

}


// =====================================
// Show Message
// =====================================

function showMessage(
    title,
    message
) {

    answerElement.innerHTML = `

        <div class="empty-state">

            <div class="empty-icon">
                ✦
            </div>

            <h4>
                ${escapeHtml(title)}
            </h4>

            <p>
                ${escapeHtml(message)}
            </p>

        </div>

    `;

}


// =====================================
// Escape HTML
// =====================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}