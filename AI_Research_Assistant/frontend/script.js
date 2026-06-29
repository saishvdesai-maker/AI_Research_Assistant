
async function register() {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    document.getElementById("msg").innerText = data.message;
}


async function login() {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    document.getElementById("msg").innerText = data.message;

    if (data.access_token) {

        localStorage.setItem("token", data.access_token);

        document.getElementById("auth-box").style.display = "none";
        document.getElementById("chat-box").style.display = "block";
    }
}


async function askQuestion() {

    const q = document.getElementById("question").value;

    const token = localStorage.getItem("token");

    if (!q) return;

    const chat = document.getElementById("chat");

    chat.innerHTML += "<p><b>You:</b> " + q + "</p>";

    const res = await fetch("/ask?q=" + encodeURIComponent(q), {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();

    chat.innerHTML += "<p><b>AI:</b> " + data.answer + "</p>";

    document.getElementById("question").value = "";
}


function logout() {

    localStorage.removeItem("token");

    document.getElementById("auth-box").style.display = "block";
    document.getElementById("chat-box").style.display = "none";
}