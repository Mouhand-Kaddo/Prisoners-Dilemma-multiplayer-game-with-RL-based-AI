document.addEventListener('DOMContentLoaded', () =>{
    var socket = io();
    // disable coop and defect buttons until message is sent
    document.querySelector('#coop').disabled = true;
    document.querySelector('#defect').disabled = true;

    // Register the session-id upon connection
    socket.on('connect', ()=>{
        socket.emit('register sid', username);
        socket.emit('Left', username);
        console.log(`https://${document.domain}/EndGame`)

        
    })
    // On closing the windows, make sure the game is closed properly
    window.onunload = (event) => {
        if (gameIsOver == false){
            navigator.sendBeacon("/end", "1");
        }
        console.log('The page is unloaded');
    };

    // Display the message upon receipt of message
    socket.on('message', data=>{
        var u = ``
        if(data.un == username){
            u = username
        }
        else{
            u = `Player 2`
        }
        var s = `${u}: ${data.mes}`
        const p = document.createElement('p');
        const br = document.createElement('br');
        p.innerHTML = s;
        document.querySelector('#dsply_msgs').append(p);
    })

    // Lock buttons from server
    socket.on('lock', data=>{
        document.querySelector('#coop').disabled = true;
        document.querySelector('#defect').disabled = true;
    })

    // End the game from server
    socket.on('end game', data=>{
        document.querySelector('#coop').disabled = true;
        document.querySelector('#defect').disabled = true;
        document.querySelector('#send_msg').disabled = true;
        gameIsOver = true;
        const p = document.createElement('p');
        p.innerHTML = `Game has ended`;
        document.querySelector('#dsply_msgs').append(p);
    })

    // Unlock buttons from server
    socket.on('unlock', data=>{
        document.querySelector('#coop').disabled = false;
        document.querySelector('#defect').disabled = false;
    })

    // Unlock send button from server
    socket.on('unlock send', data=>{
        console.log(data)
        document.querySelector('#send_msg').disabled = false;
    })

    // Display score from server
    socket.on('score', data=>{
        var u = ``
        if(data.un == username){
            u = username
        }
        else{
            u = `Player 2`
        }
        var s = `${u} Has a score of: ${data.mes}`
        const p = document.createElement('p');
        const br = document.createElement('br');
        p.innerHTML = s;
        document.querySelector('#dsply_msgs').append(p);
    })

    // Coop click
    document.querySelector('#coop').onclick = () =>{
        socket.emit('action',{'msg':`cooperated`,'username':username, 'act':`0`});
        lockAction();
    }

    // Defect click
    document.querySelector('#defect').onclick = () =>{
        socket.emit('action',{'msg':`defected`,'username':username, 'act':`1`});
        lockAction();
    }

    // Send the message to server
    document.querySelector('#send_msg').onclick = () =>{
        // Get all checked boxes
        var checkedBoxes = GetCheckedBoxes("mycb");
        // Append their values to string
        var mes = "";
        for (var i=0; i<checkedBoxes.length; i++) {
            mes = mes.concat(";", checkedBoxes[i].value)
        }
        var checkedradios = GetCheckedRadios();
        for (var i=0; i<checkedradios.length; i++) {
            mes = mes.concat(";", checkedradios[i].value)
        }
        mes = mes.substring(1);
        socket.send({'msg':mes,'username':username});
        // socket.send({'msg':document.querySelector('#usr_msg').value,'username':username});
        document.querySelector('#usr_msg').value = '';
        document.querySelector('#send_msg').disabled = true;
    }

    // Lock action input
    function lockAction(){
        document.querySelector('#coop').disabled = true;
        document.querySelector('#defect').disabled = true;
    }
    function GetCheckedBoxes(chkboxName){
        var checkboxes = document.getElementsByName(chkboxName);
        var checkboxesChecked = [];
        // loop over them all
        for (var i=0; i<checkboxes.length; i++) {
            // And stick the checked ones onto an array...
            if (checkboxes[i].checked) {
                checkboxesChecked.push(checkboxes[i]);
            }
        }
        // Return the array if it is non-empty, or null
        return checkboxesChecked.length > 0 ? checkboxesChecked : [];
    }

    function GetCheckedRadios(){
        var radios = [];
        var cradios = [];
        var radios = document.querySelectorAll('input[type=radio]');
        for (var i=0; i<radios.length; i++) {
            // And stick the checked ones onto an array...
            if (radios[i].checked) {
                cradios.push(radios[i]);
            }
        }
        return cradios.length > 0 ? cradios : [];
    }
    
})
