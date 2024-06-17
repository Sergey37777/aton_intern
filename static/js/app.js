function login() {
    // Эмуляция входа
    document.getElementById('login-btn').style.display = 'none';
    document.getElementById('logout-btn').style.display = 'inline';
    document.getElementById('user-greeting').style.display = 'inline';
    document.getElementById('clients-table').style.display = 'table';
    // Здесь должна быть логика заполнения таблицы данными, полученными от сервера
}

function logout() {
    // Эмуляция выхода
    document.getElementById('login-btn').style.display = 'inline';
    document.getElementById('logout-btn').style.display = 'none';
    document.getElementById('user-greeting').style.display = 'none';
    document.getElementById('clients-table').style.display = 'none';
}

// script.js
document.getElementById('login-btn').onclick = function() {
    document.getElementById('login-form').style.display = 'block';
}

document.getElementById('register-btn').onclick = function() {
    document.getElementById('register-form').style.display = 'block';
}

document.getElementsByClassName('close')[0].onclick = function() {
    document.getElementById('login-form').style.display = 'none';
}

document.getElementsByClassName('close')[1].onclick = function() {
        document.getElementById('register-form').style.display = 'none';
}

// Закрыть, если клик вне окна
window.onclick = function(event) {
    if (event.target === document.getElementById('login-form') ||
        event.target === document.getElementById('register-form')) {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'none';
    }
}

document.querySelector('#login-form form').onsubmit = async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const plainFormData = Object.fromEntries(formData.entries());
    const formBody = new URLSearchParams(plainFormData);

    const response = await fetch('/auth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formBody
    });

    if (response.ok) {
        const data = await response.json();
        document.cookie = `access_token=${data.access_token}; path=/; secure; HttpOnly;`;
        console.log("Login successful", data);
        console.log(data);
        console.log(data.message); // Должно вывести "Login successful"
        window.location.reload();
    } else {
        const error = await response.json();
        console.error('Login failed:', error.detail);
    }
}

document.querySelector('#register-form form').onsubmit = async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const plainFormData = Object.fromEntries(formData.entries());
    const formBody = new URLSearchParams(plainFormData);
    const response = await fetch('/auth/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formBody
    });


    if (response.ok) {
        const data = await response.json();
        console.log("Successful sign up", data);
        console.log(data);
        console.log(data.message); // Должно вывести "Login successful"
        window.location.reload();
    } else {
        const error = await response.json();
        console.error('Sign up failed:', error.detail);
    }
}


document.querySelector('#logout-btn').onclick = async function() {
    const response = await fetch('/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        console.log("Logout successful");
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        window.location.reload();
    } else {
        const error = await response.json();
        console.error('Logout failed:', error.detail);
    }

}

// Пример вызова функции для получения информации о пользователе
// getUserInfo();

