document.addEventListener('DOMContentLoaded', () =>{
    var socket = io();
    
    // Remove
    // socket.on('disconnect', ()=>{
    //     socket.emit('disfind match', username)
    // })

    socket.on('redirect', function (data) {
        window.location = data.url;
    });

    // Click on find match
    document.querySelector('#find').onclick = () =>{
        socket.emit('find match','1');
        document.querySelector('#find').disabled = true;
        
    }
    
})
