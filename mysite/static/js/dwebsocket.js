//在jquery的事件设定中插入以下连接代码，我设定的是点击button事件
$('#start').click(function () {
    //如果之前有连接则断开
    if (window.s) {
        window.s.close()
    }
    /*创建socket连接*/
    //url要在url.py中设置
    var socket = new WebSocket("ws://" + window.location.host + "/analysis/svmtraining/");
    socket.onopen = function () {
        console.log('WebSocket open');//成功连接上Websocket
    };
    socket.onmessage = function (data) {
        //这里接收服务端返回的数据
        console.log('message: ' + data.data.msg);//打印服务端返回的数据
        $('#messagecontainer').prepend('<thead><tr><th>' + data.data + '</thead></tr></th>');
    };
    // Call onopen directly if socket is already open
    if (socket.readyState == WebSocket.OPEN) socket.onopen();
    window.s = socket;
});
