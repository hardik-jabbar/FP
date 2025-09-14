const testUserRegistration = async () => {
    const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        full_name: 'Test User',
        role: 'FARMER',
        farm_type: 'crop',
        terms_accepted: true
    };

    try {
        console.log('Testing user registration...');
        const response = await fetch('https://fp-mipu.onrender.com/api/v1/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        console.log('Response status:', response.status);
        console.log('Response data:', data);
    } catch (error) {
        console.error('Error:', error.message);
    }
};

testUserRegistration();