class Chatbox {
    constructor() {
        // The args object contains references to all the necessary HTML elements.
        this.args = {
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            chatMessages: document.querySelector('.chatbox__messages')
        };

        // Initially, the chatbox is not active.
        this.state = false;
        // This will hold the conversation messages.
        this.messages = [];
    }

    display() {
        const { sendButton } = this.args;

        // Add an event listener for the send button.
        sendButton.addEventListener('click', () => this.onSendButton());

        // Add an event listener for the input field to handle the "Enter" key.
        const node = this.args.chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton();
            }
        });
    }

    onSendButton() {
        var textField = this.args.chatBox.querySelector('input');
        let text1 = textField.value;
        if (text1 === "") {
            return; // Don't send empty messages.
        }

        // Create a message object for the user's input.
        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText(); // Update the chat display.
        textField.value = ''; // Clear the input field.

        // Send the user's message to the Flask backend.
        fetch('/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            // Create a message object for the bot's response.
            let msg2 = { name: "Sam", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(); // Update the chat display.
        }).catch((error) => {
            console.error('Error:', error);
            // Even if there's an error, update the chat to show the user's message.
            this.updateChatText();
        });
    }

    updateChatText() {
        var html = '';
        // **THE FIX IS HERE:** We no longer reverse the messages array.
        // We now loop through them in their natural order.
        this.messages.forEach(function(item, index) {
            if (item.name === "Sam") { // Bot's message
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            } else { // User's message
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });

        const chatmessage = this.args.chatMessages;
        chatmessage.innerHTML = html;
        // This line will now correctly scroll to the bottom to show the latest message.
        chatmessage.scrollTop = chatmessage.scrollHeight;
    }
}

// Create a new Chatbox instance and display it.
const chatbox = new Chatbox();
chatbox.display();

