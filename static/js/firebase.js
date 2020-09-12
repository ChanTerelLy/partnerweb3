// Your web app's Firebase configuration
var firebaseConfig = {
    apiKey: "AIzaSyBU1BxUS0t23biciabryhILTccxZlnMkI0",
    authDomain: "partnerweb3-285816.firebaseapp.com",
    databaseURL: "https://partnerweb3-285816.firebaseio.com",
    projectId: "partnerweb3-285816",
    storageBucket: "partnerweb3-285816.appspot.com",
    messagingSenderId: "166059741652",
    appId: "1:166059741652:web:be532d917b9557ea9e0641",
    measurementId: "G-YF11CTXN7Y"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// [START get_messaging_object]
// Retrieve Firebase Messaging object.
const messaging = firebase.messaging();
// [END get_messaging_object]

// IDs of divs that display Instance ID token UI or request permission UI.
const tokenDivId = 'token_div';
const permissionDivId = 'permission_div';

// [START refresh_token]
// Callback fired if Instance ID token is updated.
messaging.onTokenRefresh(function () {
    messaging.getToken()
        .then(function (refreshedToken) {
            console.log('Token refreshed.');
            // Indicate that the new Instance ID token has not yet been sent to the
            // app server.
            setTokenSentToServer(false);
            // Send Instance ID token to app server.
            sendTokenToServer(refreshedToken);
            // [START_EXCLUDE]
            // Display new Instance ID token and clear UI of all previous messages.
            resetUI();
            // [END_EXCLUDE]
        })
        .catch(function (err) {
            console.log('Unable to retrieve refreshed token ', err);
        });
});
// [END refresh_token]

function resetUI() {
    // [START get_token]
    // Get Instance ID token. Initially this makes a network call, once retrieved
    // subsequent calls to getToken will return from cache.

    console.log("getting token")
    messaging.getToken().then((resp) => {
        console.log(resp)
    })
    messaging.getToken()
        .then(function (currentToken) {
            console.log("Got current token")
            if (currentToken) {
                sendTokenToServer(currentToken);
                updateUIForPushEnabled(currentToken);
            } else {
                // Show permission request.
                console.log('No Instance ID token available. Request permission to generate one.');
                // Show permission UI.
                updateUIForPushPermissionRequired();
                setTokenSentToServer(false);
            }
        })
        .catch(function (err) {
            console.log('An error occurred while retrieving token. ', err);
            setTokenSentToServer(false);
        });
    console.log("End get token")

}

// [END get_token]


// Send the Instance ID token your application server, so that it can:
// - send messages back to this app
// - subscribe/unsubscribe the token from topics
function registerDevice(currentToken) {
    return $.ajax({
        url: `/devices/`,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
              xhr.setRequestHeader("X-CSRFToken", csrf_token);
          },
        data: JSON.stringify({
            'registration_id': currentToken,
            'type': 'web',
            'device_id': $('#agent').text()
        }),
        dataType: 'json',
        success: function (data) {
            return data
        }
    })
}

function sendTokenToServer(currentToken) {
    if (!isTokenSentToServer()) {
        console.log('Sending token to server...');
        registerDevice(currentToken).then(function (response) {
            alert("Вы успешно подписаны!");
        })
        setTokenSentToServer(true);
    } else {
        console.log('Token already sent to server so won\'t send it again ' +
            'unless it changes');
    }

}

function isTokenSentToServer() {
    if (window.localStorage.getItem('sentToServer') == 1) {
        return true;
    }
    return false;
}

function setTokenSentToServer(sent) {
    if (sent) {
        window.localStorage.setItem('sentToServer', 1);
    } else {
        window.localStorage.setItem('sentToServer', 0);
    }
}

function requestPermission() {
    console.log('Requesting permission...');
    // [START request_permission]
    messaging.requestPermission()
        .then(function () {
            console.log('Notification permission granted.');
        })
        .catch(function (err) {
            console.log('Unable to get permission to notify.', err);
        });
    // [END request_permission]
}

resetUI();
