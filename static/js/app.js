(function connect() {
    // console.log(location);
    let socket = io.connect(location.host);
    $("#usernameBtn").click(function () {
        console.log($("#username").val());
        socket.emit('change_username', { username: $("#username").val() });
        $(".card-header").text($("#username").val());
        localStorage.testUsername = $("#username").val();
        $("#username").val('');
    });
    $('#messageBtn').click(function () {
        send_message();
    });
    $('#message').keypress(function (e) {
        socket.emit('typing');
        if (e.which === 13) {
            send_message();
        }
    });
    socket.on('connect',()=>{
        console.log("Connected as Anonymous")
        if (localStorage.testUsername) {
            socket.emit('change_username', { username: localStorage.testUsername });
            $(".card-header").text(localStorage.testUsername)
            console.log(`Connected as ${localStorage.testUsername}`)
        }
    });
    socket.on('typing', data => {
        $(".info").text(data.username + " is typing...");
        setTimeout(() => { $(".info").text("") }, 5000)
    });
    socket.on('receive_message', data => {
        console.log(data);
        $("#message-list").append(`<li class="list-group-item">${data.username}:${data.message}</li>`);
    });
    function send_message(){
        console.log($('#message').val());
        socket.emit('new_message', { message: $('#message').val() });
        $('#message').val("")
    }
})();