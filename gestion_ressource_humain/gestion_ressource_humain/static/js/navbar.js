// Function to handle button clicks
function handleButtonClick(event) {
  // Check which button was clicked and navigate to the corresponding page
  if (event.target.id === "loginBtn") {
    window.location.href = "../login"; // Navigate to the login page
  } else if (event.target.id === "logupBtn") {
    window.location.href = "..//signup"; // Navigate to the signup page
  }
}

// Add event listeners to both buttons
document
  .getElementById("loginBtn")
  .addEventListener("click", handleButtonClick);
document
  .getElementById("logupBtn")
  .addEventListener("click", handleButtonClick);
