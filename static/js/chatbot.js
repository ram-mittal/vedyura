class Chatbox {
    constructor() {
        this.args = {
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            chatMessages: document.querySelector('.chatbox__messages')
        };
        this.state = false;
        this.messages = [];
    }

    display() {
        const { sendButton } = this.args;
        sendButton.addEventListener('click', () => this.onSendButton(null));

        const node = this.args.chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(null);
            }
        });
    }

    // New function to handle button clicks
    handleButtonClick(text) {
        this.onSendButton(text);
    }

    onSendButton(buttonText) {
        var textField = this.args.chatBox.querySelector('input');
        // Use the button's text if it was clicked, otherwise use the input field's text.
        let text1 = buttonText || textField.value;
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText();
        textField.value = '';

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
            let msg2 = { name: "Sam", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText();
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText();
        });
    }

    updateChatText() {
        var html = '';
        this.messages.forEach((item) => {
            let messageHtml = item.message;
            
            // This is the new logic to find and replace our button syntax.
            const buttonRegex = /\[button:(.*?)\]/g;
            messageHtml = messageHtml.replace(buttonRegex, (match, buttonText) => {
                return `<button class="chat-button">${buttonText}</button>`;
            });

            if (item.name === "Sam") { // Bot's message
                html += `<div class="messages__item messages__item--visitor">${messageHtml}</div>`
            } else { // User's message
                html += `<div class="messages__item messages__item--operator">${messageHtml}</div>`
            }
        });

        const chatmessage = this.args.chatMessages;
        chatmessage.innerHTML = html;

        // Add event listeners to the newly created buttons.
        chatmessage.querySelectorAll('.chat-button').forEach(button => {
            button.addEventListener('click', () => {
                this.handleButtonClick(button.textContent);
            });
        });

        chatmessage.scrollTop = chatmessage.scrollHeight;
    }
}

const chatbox = new Chatbox();
chatbox.display();

