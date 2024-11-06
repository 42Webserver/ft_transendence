import { getCookie, displayMessages } from './utils.js';
import { showSection } from './index.js';

export async function renderSettings() {

	const app = document.getElementById('app');
	app.innerHTML = `
	<div class="login">
		<div class="login-container">
			<form id="settingsForm" enctype="multipart/form-data">
				<input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
				<div class="login-instructions">
					<p>Update your account information!</p>
				</div>
				
				<div class="login-form-field">
                    <label for="floatingInput" class="settings-label">Email address</label>
					<input id="settings-email" type="email" name="email" class="form-control" placeholder="name@example.com">
				</div>
				<div class="login-form-field">
                    <label for="floatingPassword" class="settings-label">New password</label>
					<input type="password" name="password" class="form-control" placeholder="Password">
				</div>
				<div class="login-form-field">
                    <label for="floatingPassword" class="settings-label">Confirm new password</label>
					<input type="password" name="password" class="form-control" placeholder="Password">
				</div>
				<div class="login-form-field">
                    <label for="floatingPassword" class="settings-label">Firstname</label>
					<input id="settings-firstname" type="text" name="firstname" class="form-control" placeholder="Firstname">
				</div>
				<div class="login-form-field">
                	<label for="floatingPassword" class="settings-label">Lastname</label>
					<input id="settings-lastname" type="text" name="lastname" class="form-control" placeholder="Lastname">
				</div>
				<div class="login-form-field">
                    <label for="floatingPassword" class="settings-label">Username</label>
					<input id="settings-username" type="text" name="username" class="form-control" placeholder="Username">
				</div>
				<div class="login-form-field form-floating">
					<input type="file" name="avatar" class="form-control" placeholder="Upload avatar">
					<label for="floatingInput">Upload avatar</label>
				</div>	
				<button class="signin-button btn btn-primary w-100 py-2" type="submit">Update</button>	
				<div id="settingsMessage" class="register-message"></div>
			</form>
		</div>
		<div id="settingsLoader" class="loader"></div> 	
	</div>
	`;
    const inputEmail = document.getElementById('settings-email');
    const inputFirstname = document.getElementById('settings-firstname');
    const inputLastname = document.getElementById('settings-lastname');
    const inputUsername = document.getElementById('settings-username');

    const response = await getUserInformation();
    if (response.error)
        displayMessages(response);
    else
    {
        inputEmail.value = response.email;
        inputFirstname.value = response.firstname;
        inputLastname.value = response.lastname;
        inputUsername.value = response.username;
    }    
	const form = document.getElementById('settingsForm');
    form.addEventListener('submit', handleSettingsFormSubmit);

}

async function getUserInformation() {
    try {
		const token = localStorage.getItem('access_token'); 

        const response = await fetch(`/get_user_information/`, {
            method: 'GET',
			headers: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json'
			}
        });
        return await response.json();
    }
    catch(error){
        return ({'error': 'Request for getting settings failed.'});
    }
}

async function handleSettingsFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
	
    const token = localStorage.getItem('access_token'); 
	
    const response = await fetch('/settings/', {
		method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: formData//JSON.stringify(data)
    });
	
    const result = await response.json();
	console.log("result: ", result);

	const settingsMessage = document.getElementById('settingsMessage');
	
	if (result.type === 'success')
	{
		settingsMessage.textContent = '';

		const settingsLoader = document.getElementById('settingsLoader');
		settingsLoader.style.display = 'block';

		setTimeout(() => showSection('menu'), 2000);
	}
	else
	{
		settingsMessage.textContent = result.message;
		settingsMessage.style.color = 'red';
		settingsMessage.style.animation = 'none';
		settingsMessage.offsetHeight;
		settingsMessage.style.animation = 'wiggle 0.5s ease-in-out';
	}

}