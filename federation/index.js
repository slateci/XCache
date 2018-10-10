var express = require('express');
var https = require('https');
var http = require('http');


var bodyParser = require('body-parser');



const elastic = require('./elastic.js');
const server = require('./server.js');

// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests",
    SIMULATION: true
};

console.log('XCache backend server starting ... ');


const app = express();

app.use(express.static('public'));
// app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json('application/json'));

var requests = [];
var server_set;

String.prototype.hashCode = function () {
    var hash = 0, i, chr;
    if (this.length === 0) return hash;
    for (i = 0; i < this.length; i++) {
        chr = this.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

/*
 requires client site (how defined ?) and origin server site (how defined?)
 to test do wget localhost:8080/path/aod.root/MWT2/BNL
 or curl -X GET "localhost:8080/path/asdf/asdf/asddf"
*/
app.get('/path/:filename/:edgecache/:originpath', function (req, res) {
    console.log('got path request');
    // console.log(req.params.filename, req.params.edgecache, req.params.originpath);
    requests.push({
        filename: req.params.filename,
        edgecache: req.params.edgecache,
        origin: req.params.originpath,
        timestamp: new Date().getTime()
    });

    if (requests.length > 1) {
        var es = new elastic();
        es.save_requests(requests);
        requests = [];
    }
    res.status(200).send('OK');
});

app.get('/simulate/:filename/:edgecache/:filesize', function (req, res) {
    console.log('got path request');
    // console.log(req.params.filename, req.params.edgecache, req.params.filesize);
    request = {
        filename: req.params.filename.hashCode(),
        edgecache: req.params.edgecache,
        filesize: req.params.filesize
    };
    console.log(request);
    res.status(200).send('OK');
});

// add function that serves clients based on their geoip.
// req.connection.remoteAddress
// could hold cache of proximity for known addresses.

app.post('/add_server', async function (req, res) {
    console.log('adding server');
    var serv = new server()
    if (!serv.initialize(req.body)) {
        res.status(400).send({ error: 'Not all required parameters provided.' });
    } else {
        var es = new elastic();
        await es.add_server(serv);
        await reload_servers();
        res.status(200).send('OK');
    }
});

/* 
will update everything except: index, site, long, lat, 
*/
app.post('/update_server', async function (req, res) {
    console.log('updating server');
    // console.log(req.body);
    var es = new elastic();
    await es.update_server(req.body);
    await reload_servers();
    res.status(200).send('OK');
});

app.delete('/server/:server_id', async function (req, res) {
    console.log('removing server');
    console.log(req.params.server_id);
    var es = new elastic();
    await es.delete_server(req.params.server_id);
    await reload_servers();
    res.status(200).send('OK');
});





app.use((err, req, res, next) => {
    console.error('Error in error handler: ', err.message);
    res.status(err.status).send(err.message);
});


async function reload_servers() {
    console.log('reloading servers');
    var es = new elastic();
    server_set = await es.load_server_tree();
}


// var httpsServer = https.createServer(credentials, app).listen(443);

//// redirects to https if someone comes on http.
// http.createServer(function (req, res) {
//     res.writeHead(302, { 'Location': 'https://' + config.SITENAME });
//     res.end();
// }).listen(80);

// for testing
var httpsServer = http.createServer(app).listen(8080);

async function main() {
    try {
        await reload_servers();
        // console.log("---------------\n", server_set);
    } catch (err) {
        console.error('Error: ', err);
    }
}

main();