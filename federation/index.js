var express = require('express');
var https = require('https');
var http = require('http');


var bodyParser = require('body-parser');



const elastic = require('./elastic.js');

// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xcache-servers",
    REQUESTS_INDEX: "xcache-requests"
};

console.log('XCache backend server starting ... ');


const app = express();

app.use(express.static('public'));
// app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json('application/json'));

var requests = [];


/*
 requires client site (how defined ?) and origin server site (how defined?)
 to test do wget localhost:8080/path/aod.root/MWT2/BNL
 or curl -X GET "localhost:8080/path/asdf/asdf/asddf"
*/
app.get('/path/:filename/:client/:origin', function (req, res) {
    console.log('got path request');
    // console.log(req.params.filename, req.params.client, req.params.origin);
    requests.push({
        filename: req.params.filename,
        client: req.params.client,
        origin: req.params.origin,
        timestamp: new Date().getTime()
    });

    if (requests.length > 1) {
        var es = new elastic();
        es.save_requests(requests);
        requests = [];
    }
    res.status(200).send('OK');
});

// add function that serves clients based on their geoip.
// req.connection.remoteAddress
// could hold cache of proximity for known addresses.

// to test do: curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @server.json
app.post('/add_server', function (req, res) {
    console.log('adding server');
    // console.log(req.body); 
    var es = new elastic();
    es.save_requests(req.body);
    res.status(200).send('OK');
});

app.delete('/remove_server/:server', function (req, res) {
    console.log('removing server');
    console.log(req.params.server);
    res.status(200).send('OK');

    // res.json({
    //     TFAAS: ml_front_config.TFAAS,
    //     PUBLIC_INSTANCE: ml_front_config.PUBLIC_INSTANCE,
    //     MONITOR: ml_front_config.MONITOR
    // });
});





app.use((err, req, res, next) => {
    console.error('Error in error handler: ', err.message);
    res.status(err.status).send(err.message);
});


// var httpsServer = https.createServer(credentials, app).listen(443);

//// redirects to https if someone comes on http.
// http.createServer(function (req, res) {
//     res.writeHead(302, { 'Location': 'https://' + config.SITENAME });
//     res.end();
// }).listen(80);

// for testing
var httpsServer = http.createServer(app).listen(8080);
