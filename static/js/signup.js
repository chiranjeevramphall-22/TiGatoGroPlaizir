// =====================================================
// SIGNUP PAGE INTERACTIVITY
// Makes the suggested username clickable.
// =====================================================
document.addEventListener("DOMContentLoaded", function() {
    // Find the username input and the error message box
    const usernameInput = document.getElementById('id_username');
    const errorBox = document.querySelector('.error-message');

    // Check if the error box exists and contains a suggestion
    if (errorBox && errorBox.innerText.includes("Try '")) {
        // Use regex to extract the suggested username from the error text
        const match = errorBox.innerText.match(/Try '([^']+)' instead/);
        
        if (match && match[1]) {
            const suggestion = match[1];
            
            // Create a clickable button for the suggestion
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.innerText = `Use '${suggestion}'`;
            // Style the button so it looks like a small "chip"
            btn.style.cssText = 'margin-left: 10px; padding: 4px 8px; font-size: 11px; background: #d19a7a; color: white; border: none; border-radius: 4px; cursor: pointer;';
            
            // When clicked, fill the username input and hide the error
            btn.addEventListener('click', function() {
                usernameInput.value = suggestion;
                errorBox.style.display = 'none';
            });
            
            // Add the button inside the error box
            errorBox.appendChild(btn);
        }
    }
});