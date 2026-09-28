document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');
    
    // Basic validation
    if (!email || !password) {
        messageDiv.textContent = 'Please fill in all fields';
        messageDiv.className = 'message error';
        return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        messageDiv.textContent = 'Please enter a valid email address';
        messageDiv.className = 'message error';
        return;
    }
    
    // Password validation (minimum 6 characters)
    if (password.length < 6) {
        messageDiv.textContent = 'Password must be at least 6 characters';
        messageDiv.className = 'message error';
        return;
    }
    
    // Send data to backend
    const data = {
        email: email,
        password: password,
        remember: document.querySelector('input[name="remember"]').checked
    };
    
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageDiv.textContent = 'Login successful!';
            messageDiv.className = 'message success';
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            messageDiv.textContent = data.message || 'Login failed. Please try again.';
            messageDiv.className = 'message error';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        messageDiv.textContent = 'An error occurred. Please try again.';
        messageDiv.className = 'message error';
    });
});
