console.log("Hello from whore.ai")
        let lastTapTime = 0;
        const doubleTapDelay = 300; // milliseconds

        function handleDoubleTap(event, imageName) {
            const currentTime = new Date().getTime();
            const tapTime = currentTime - lastTapTime;
            if (tapTime < doubleTapDelay && tapTime > 0) {
                // Double tap detected, save the image as favorite
                saveAsFavorite(imageName);
                event.preventDefault(); // Prevents zooming on double tap
            }
            lastTapTime = currentTime;
        }

        function saveAsFavorite(imageName) {
            fetch(`/save-favorite/${imageName}`, { method: 'POST' });
        }


        document.getElementById("floating-form").addEventListener("submit", async (event) => {
            event.preventDefault();

            const inputBox = document.getElementById("new-line");
            const newLine = inputBox.value;

            const response = await fetch("/update-prompt", {
                method: "PUT",
                body: newLine
            });

            if (response.ok) {
                const jsonResponse = await response.json();
                alert(jsonResponse.message);
                inputBox.value = "";
            } else {
                alert("Failed to add a new line.");
            }
        });

        document.getElementById("edit-prompt").addEventListener("click", () => {
            window.location.href = "/edit-prompt";
        });