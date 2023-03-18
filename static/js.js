function fetchMessages() {
  // Fetch the latest messages from the server using AJAX
  fetch('/get-messages')
    .then(response => response.text())
    .then(html => {
      // Replace the contents of the messages container with the new HTML
	  var temp = html.getElementById('chat-bubble').innerHTML;
      document.getElementById('messages-container').innerHTML = temp;
    })
    .catch(error => console.error(error));
}

// Call the fetchMessages function every 5 seconds
//setInterval(fetchMessages, 1000);