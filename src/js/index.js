import { handleLogoutSubmit } from './utils.js';

let wsBool;
wsBool = false;

let ws;
async function checkAuthentication() {
    const response = await fetch('/checkauth/', {
        method: 'GET',
        credentials: 'include'  // Ensure cookies are included in the request
    });
    const result = await response.json();
    if (result.authenticated) {
        localStorage.setItem('authenticated', 'true');
        localStorage.setItem('user', JSON.stringify(result.user));
    } else {
        localStorage.removeItem('authenticated');
        localStorage.removeItem('user');
    }
    return result.authenticated;
}

async function renderLoginLogoutButton(isAuthenticated, section) {

    const app = document.getElementById('LoginLogoutButton');
    if (!app)
        return;
        
    if (isAuthenticated)
    {
        app.innerHTML = `
        <div class="col-5">
        <button id="logoutButton" type="button" class="btn btn-primary login-logout-button">Logout</button>
        </div>
        `;
        const logoutButton = document.getElementById('logoutButton')
        logoutButton.addEventListener('click', () => {
            wsBool = false;
            handleLogoutSubmit(ws, wsBool);
        });
    }
    else
    {
        if (section === 'register')
        {
            app.innerHTML = `
            <div class="col-5">
            <button id="loginButton" type="button" class="btn btn-primary login-logout-button">Login</button>
            </div>
            `;
            const loginButton = document.getElementById('loginButton')
            loginButton.addEventListener('click', () => {
                showSection('login');
            });
        }
        else //(section === 'login')
        {
            app.innerHTML = `
            <div class="col-5">
            <button id="registerButton" type="button" class="btn btn-primary login-logout-button">Sign up</button>
            </div>
            `;
            const registerButton = document.getElementById('registerButton')
            registerButton.addEventListener('click', () => {
                showSection('register');
            });
        }

    }
}

function addListItem(content, ul, list)
{
    const li = document.createElement('li');

    const friendsModifyModal = document.getElementById('friendsModifyModal');
    const closeModalButton = document.getElementById('closeFriendsModifyModalButton');
    const friendsModifyModalUsername = document.getElementById('friendsModifyModalUsername');
    const removeFriendButton = document.getElementById('removeFriendButton');
    const blockFriendButton = document.getElementById('blockFriendButton');
    const acceptFriendButton = document.getElementById('acceptFriendButton');
    const denyFriendButton = document.getElementById('denyFriendButton');
    const withdrawFriendButton = document.getElementById('withdrawFriendButton');
    const unblockFriendButton = document.getElementById('unblockFriendButton');

    if (!friendsModifyModal || !closeModalButton)
        return;

    friendsModifyModalUsername.textContent = "\"" + content + "\"";
    friendsModifyModalUsername.style.color = '#1792ca';

    if (list === 'offline' || list === 'online')
    {
        li.className = 'friends-add-list-user';
        li.innerHTML = `<span class="list-item-content">${content}</span>`;
        ul.appendChild(li);

        const textSpan = li.querySelector('.list-item-content');

        textSpan.addEventListener('click', () => {
            friendsModifyModal.style.display = 'block';
            removeFriendButton.style.display = 'block';
            blockFriendButton.style.display = 'block';
            friendsModifyModalUsername.textContent = "\"" + content + "\"";
        });

        closeModalButton.addEventListener('click', () => {
            friendsModifyModal.style.display = 'none';
            removeFriendButton.style.display = 'none';
            blockFriendButton.style.display = 'none';
        });
    
        window.addEventListener('click', (event) => {
            if (event.target === friendsModifyModal) {
                friendsModifyModal.style.display = 'none';
                removeFriendButton.style.display = 'none';
                blockFriendButton.style.display = 'none';
            }
        });
    }
    else if (list === 'request')
    {
        li.className = 'friends-add-list-user';
        li.innerHTML = `<span class="list-item-content">${content}</span>`;
        ul.appendChild(li);

        const textSpan = li.querySelector('.list-item-content');

        textSpan.addEventListener('click', () => {
            friendsModifyModal.style.display = 'block';
            acceptFriendButton.style.display = 'block';
            denyFriendButton.style.display = 'block';
            blockFriendButton.style.display = 'block';
            friendsModifyModalUsername.textContent = "\"" + content + "\"";
        });

        closeModalButton.addEventListener('click', () => {
            friendsModifyModal.style.display = 'none';
            acceptFriendButton.style.display = 'none';
            denyFriendButton.style.display = 'none';
            blockFriendButton.style.display = 'none';
        });
    
        window.addEventListener('click', (event) => {
            if (event.target === friendsModifyModal) {
                friendsModifyModal.style.display = 'none';
                acceptFriendButton.style.display = 'none';
                denyFriendButton.style.display = 'none';
                blockFriendButton.style.display = 'none';
            }
        });
    }
    else if (list === 'pending')
    {
        li.className = 'friends-add-list-user';
        li.innerHTML = `<span class="list-item-content">${content}</span>`;
        ul.appendChild(li);

        const textSpan = li.querySelector('.list-item-content');

        textSpan.addEventListener('click', () => {
            friendsModifyModal.style.display = 'block';
            withdrawFriendButton.style.display = 'block';
            blockFriendButton.style.display = 'block';
            friendsModifyModalUsername.textContent = "\"" + content + "\"";
        });

        closeModalButton.addEventListener('click', () => {
            friendsModifyModal.style.display = 'none';
            withdrawFriendButton.style.display = 'none';
            blockFriendButton.style.display = 'none';
        });
    
        window.addEventListener('click', (event) => {
            if (event.target === friendsModifyModal) {
                friendsModifyModal.style.display = 'none';
                withdrawFriendButton.style.display = 'none';
                blockFriendButton.style.display = 'none';
            }
        });
    }
    else if (list === 'blocked')
    {
        li.className = 'friends-add-list-user';
        li.innerHTML = `<span class="list-item-content">${content}</span>`;
        ul.appendChild(li);

        const textSpan = li.querySelector('.list-item-content');

        textSpan.addEventListener('click', () => {
            friendsModifyModal.style.display = 'block';
            unblockFriendButton.style.display = 'block';
            friendsModifyModalUsername.textContent = "\"" + content + "\"";
        });

        closeModalButton.addEventListener('click', () => {
            friendsModifyModal.style.display = 'none';
            unblockFriendButton.style.display = 'none';
        });
    
        window.addEventListener('click', (event) => {
            if (event.target === friendsModifyModal) {
                friendsModifyModal.style.display = 'none';
                unblockFriendButton.style.display = 'none';
            }
        });
    }
    else
    {
        li.className = 'friends-add-list-user';
        li.innerHTML = `<span class="list-item-content">${content}</span>`;
        ul.appendChild(li);
    }
}

function initOnlineStatus() {
    ws = new WebSocket(`ws://${window.location.host}/ws/online-status/`);

    ws.onopen =  function() {
        console.log("Connected to WebSocket Online Status");
    };

    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            const friendsOnlineList = document.getElementById('friendsOnlineList');
            const friendsOfflineList = document.getElementById('friendsOfflineList');
            const friendsPendingList = document.getElementById('friendsPendingList');
            const friendsRequestsList = document.getElementById('friendsRequestsList'); 
            const friendsBlockedList = document.getElementById('friendsBlockedList'); 
                
            if (!friendsOnlineList || !friendsOfflineList || !friendsPendingList || !friendsRequestsList || !friendsBlockedList)
                return;

            friendsOnlineList.innerHTML = "";
            friendsOfflineList.innerHTML = "";
            friendsPendingList.innerHTML = "";
            friendsRequestsList.innerHTML = "";
            friendsBlockedList.innerHTML = "";

            console.log("data: ", data.friendList);
            
            const freundesliste = data.friendList;
            
            console.log("freundesliste len: ", freundesliste.length);
            console.log("freundesliste: ", freundesliste);
            
            console.log("freund[0]: ", freundesliste[0]);
            console.log("freund[0].status: ", freundesliste[0].status);
            console.log("freund[0].username: ", freundesliste[0].username);


            for (let i = 0; i < freundesliste.length; i++)
            {
                console.log("friend: ", freundesliste[i].username);

                if (freundesliste[i].status === 'online')
                    addListItem(freundesliste[i].username, friendsOnlineList, 'online');
                else if (freundesliste[i].status === 'offline')
                    addListItem(freundesliste[i].username, friendsOfflineList, 'offline');
                else if (freundesliste[i].status === 'pending' && freundesliste[i].type === 'sender')
                    addListItem(freundesliste[i].username, friendsPendingList, 'pending');
                else if (freundesliste[i].status === 'pending' && freundesliste[i].type === 'receiver')
                    addListItem(freundesliste[i].username, friendsRequestsList, 'request');
                else
                    addListItem(freundesliste[i].username, friendsBlockedList, 'blocked');
            }
        }
        catch (error){
            console.error("Error Parsing online status");
        }
    };

    ws.onclose = function() {
        console.log("WebSocket Online Status connection closed");
    };
}

export async function showSection(section, lobbyId)
{
    console.log('section:' + section);
    const isAuthenticated = await checkAuthentication();
    renderLoginLogoutButton(isAuthenticated, section);
    if (section === 'register')
        import('./register.js').then(module => {
            module.renderRegister();
        });
    else if (section === 'login')
        import('./login.js').then(module => {
            module.renderLogin();    
        });
    if (isAuthenticated) {
        if (!wsBool)
        {
            initOnlineStatus();
            wsBool = true;
        }
        else 
            console.log("WARUM IST ES NICHT EINGELOGGT?!");
        if (section === 'welcome')
                import('./welcome.js').then(module => {
                    module.renderWelcome();
                });
        else if (section === 'websocket')
            import('./test.js').then(module => {
                module.renderWebsocket();
            });
        else if (section === 'pong')
            import('./pong.js').then(module => {
                module.renderPong();
            });
        else if (section === 'lobby') {
            import('./lobby.js').then(module => {
                module.renderLobby(lobbyId);
            });
        }
    }
    else if (section != 'login' && section != 'register') {
        import('./login.js').then(module => {
            module.renderLogin();    
        });
        section = 'login';
    }
}


async function initApp() {
    const isAuthenticated = await checkAuthentication();
    if (isAuthenticated) {
        showSection('welcome');
    } else {
        showSection('login');
    }
}

window.addEventListener('popstate', (event) => {
	if (event.state && event.state.section){
		showSection(event.state.section);
	}
});

window.onload = initApp;
