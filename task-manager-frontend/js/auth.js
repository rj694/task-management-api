document.addEventListener('DOMContentLoaded', () => {
    // Session management
    let sessionWarningShown = false;

    function checkSessionExpiry() {
        const token = api.getToken();
        if (!token) return;
        
        try {
            // Decode JWT to check expiry (basic decode, not verification)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expiryTime = payload.exp * 1000;
            const now = Date.now();
            const timeUntilExpiry = expiryTime - now;
            
            // Warn 5 minutes before expiry
            if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0 && !sessionWarningShown) {
                sessionWarningShown = true;
                feedback.showError(
                    { message: 'Your session will expire soon. Please save your work.' },
                    ''
                );
            }
        } catch (e) {
            // Invalid token format, ignore
        }
    }

    // Check session every minute
    if (typeof feedback !== 'undefined') {
        setInterval(checkSessionExpiry, 60000);
    }

    // Handle login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            
            try {
                errorMessage.style.display = 'none';
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Logging in...';
                submitBtn.disabled = true;
                
                const data = await api.auth.login(email, password);
                
                // Save tokens and user data
                api.setToken(data.access_token);
                api.setRefreshToken(data.refresh_token);
                api.setUser(data.user);
                
                // Show success message if feedback is available
                if (typeof feedback !== 'undefined') {
                    feedback.showSuccess('Login successful! Redirecting...');
                }
                
                // Redirect to main page
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 500);
            } catch (error) {
                errorMessage.textContent = error.message.includes('Invalid credentials') 
                    ? 'Incorrect email or password. Please try again.'
                    : error.message;
                errorMessage.style.display = 'block';
                
                // Re-enable button
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                submitBtn.textContent = 'Login';
                submitBtn.disabled = false;
            }
        });
    }
    
    // Handle register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            
            try {
                errorMessage.style.display = 'none';
                const submitBtn = registerForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Creating account...';
                submitBtn.disabled = true;
                
                // Client-side validation
                if (username.length < 3) {
                    throw new Error('Username must be at least 3 characters long');
                }
                if (password.length < 8) {
                    throw new Error('Password must be at least 8 characters long');
                }
                if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                    throw new Error('Please enter a valid email address');
                }
                
                const data = await api.auth.register(username, email, password);
                
                // Save tokens and user data
                api.setToken(data.access_token);
                api.setRefreshToken(data.refresh_token);
                api.setUser(data.user);
                
                // Show success message if feedback is available
                if (typeof feedback !== 'undefined') {
                    feedback.showSuccess('Account created successfully! Redirecting...');
                }
                
                // Redirect to main page
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 500);
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
                
                // Re-enable button
                const submitBtn = registerForm.querySelector('button[type="submit"]');
                submitBtn.textContent = 'Register';
                submitBtn.disabled = false;
            }
        });
    }
    
    // Handle logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            if (typeof feedback !== 'undefined') {
                feedback.confirm(
                    'Are you sure you want to log out?',
                    async () => {
                        try {
                            const stopLoading = feedback.showLoading(logoutBtn, 'Logging out...');
                            await api.auth.logout();
                            feedback.showSuccess('Logged out successfully');
                            setTimeout(() => {
                                window.location.href = 'login.html';
                            }, 500);
                        } catch (error) {
                            console.error('Logout error:', error);
                            // Still redirect even if there's an error
                            window.location.href = 'login.html';
                        }
                    }
                );
            } else {
                // Fallback without feedback module
                if (confirm('Are you sure you want to log out?')) {
                    try {
                        await api.auth.logout();
                        window.location.href = 'login.html';
                    } catch (error) {
                        console.error('Logout error:', error);
                        window.location.href = 'login.html';
                    }
                }
            }
        });
    }
    
    // Display username in the header
    const usernameElement = document.getElementById('username');
    if (usernameElement) {
        const user = api.getUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
    }
});