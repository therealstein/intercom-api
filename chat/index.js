const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const util = require('util');
const port = 3000;
const mysql = require("mysql");
const clients = [];
const DATE_FORMATER = require( 'dateformat' );
var player = {};
//create db connection
pw = process.env.IC_DBPassword;
thedb = process.env.IC_Database;
db = mysql.createConnection({
  host: "intercom-db",
  port: "3306",
  user: "root",
  password: pw,
  database: thedb
  }),


db.connect(function(err){
	if(err){
		console.log('Error connecting to Db');
		return;
	}
	console.log('Database Connection established');
});

//Server Web Client
app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

//When a client connects, bind each desired event to the client socket
io.on('connection', function(socket){
	//track connected clients via log
	clients.push(socket.id);
	let clientConnectedMsg = 'User connected ' + util.inspect(socket.id) + ', total: ' + clients.length;
    io.emit('chat message', clientConnectedMsg);
	io.emit('player spawn', clients);
	console.log(clientConnectedMsg);

	//track disconnected clients via log
	socket.on('disconnect', function(){
		clients.pop(socket.id);
		let clientDisconnectedMsg = 'User disconnected ' + util.inspect(socket.id) + ', total: ' + clients.length;
		io.emit('chat message', clientDisconnectedMsg);
    delete player[socket.id]
		console.log(clientDisconnectedMsg);
	})

	//multicast received message from client
	socket.on('chat message', function(msg){
		let combinedMsg = socket.id.substring(0,4) + ': ' + msg;
		//io.emit('chat message', combinedMsg);
        io.emit('chat message', msg);
        var timestamp = DATE_FORMATER( new Date(), "yyyy-mm-dd HH:MM:ss" );
    	//write in mysql
		var newmes  = {fromid:util.inspect(socket.id),toid:util.inspect(socket.id),text: msg,created:timestamp};
		var query = db.query("INSERT INTO ic_chat SET ?", newmes, function(err, result) {
		//	console.log(query.sql);
			if(err) {console.log(err);}
			socket.emit('chat', { text: msg, created:timestamp });
        });
		//console.log('multicast: ' + combinedMsg);
    console.log('multicast: ' + msg);
	})
  //multicast received message from client
  socket.on('send coordinates', function(coordinates){
    io.emit('send coordinates', coordinates);
    console.log('multicast: ' + coordinates);
  })
  socket.on('player spawn', function(nickname){
    //io.emit('player spawn', socket.id);
    player[socket.id] = nickname
    io.emit('player', player);
    console.log('multicast: ' + JSON.stringify(player));
  });
});

//Start the Server
http.listen(port, function(){
  console.log('listening on *:' + port);
});
