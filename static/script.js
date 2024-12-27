

document.addEventListener("DOMContentLoaded", () => {
    const updateInterval = 1000; // Update every second

    function sendCommand(command) {
        console.log(`Sending command: ${command}`);
        fetch("/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command }),
        })
        .then(response => {
            console.log(`Response status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            updatePage(data);
        })
        .catch(error => console.error("Error sending command:", error));
    }
    
    
    function updatePage(data) {
        // Update text fields
        document.getElementById("door_current_state").innerText = data.door_current_state;
        document.getElementById("door_error_state").innerText = data.door_error_state;
        document.getElementById("door_auto_state").innerText = data.door_auto_state;
    
        document.getElementById("light_current_state").innerText = data.light_current_state;
        document.getElementById("light_auto_state").innerText = data.light_auto_state;
    
        document.getElementById("system_time").innerText = data.system_time;
    }
    
    function fetchUpdate() {
        sendCommand("update");
    }


    // Attach event listeners to buttons
    document.querySelectorAll("button[data-command]").forEach(button => {
        button.addEventListener("click", () => {
            const command = button.getAttribute("data-command");
            sendCommand(command);
        });
    });

    // Start the update loop
    setInterval(fetchUpdate, updateInterval);
});
