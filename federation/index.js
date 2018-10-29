var express = require('express');
var https = require('https');
var http = require('http');
var fs = require('fs');

var bodyParser = require('body-parser');

const elastic = require('./elastic.js');
const server = require('./server.js');
const site = require('./site.js');

var config = require('/etc/backend-conf/config.json');

// var config = {
//     SITENAME: "xcache.org",
//     ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
//     SERVERS_INDEX: "xc_servers",
//     REQUESTS_INDEX: "xc_requests",
//     STRESS_INDEX: "stress",
//     SIMULATION: true
// };

var privateKey = fs.readFileSync('/etc/https-certs/key.pem');//, 'utf8'
var certificate = fs.readFileSync('/etc/https-certs/cert.pem');

var credentials = { key: privateKey, cert: certificate };

console.log('XCache backend server starting ... ');


const app = express();

app.use(express.static('public'));
// app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json('application/json'));

var nrequests = 0;


var es = new elastic();

String.prototype.hashCode = function () {
    var hash = 0, i, chr;
    if (this.length === 0) return hash;
    for (i = 0; i < this.length; i++) {
        chr = this.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash);
};

/*
 requires client site (how defined ?) and origin server site (how defined?)
 to test do wget localhost:8080/path/aod.root/xc_MWT2/BNL
 or curl -X GET "localhost:8080/path/aod.root/xc_MWT2/root://bnl.asdf/asdf/asdf/aod.root"
*/
app.get('/path/:filename/:edgecache/:originpath', function (req, res) {
    console.log('got path request');
    // console.log(req.params.filename, req.params.edgecache, req.params.originpath);

    es.add_request({
        filename: req.params.filename,
        edgecache: req.params.edgecache,
        origin: req.params.originpath,
        timestamp: new Date().getTime()
    });

    res.status(200).send('OK');
});

app.get('/simulate', function (req, res) {
    // console.log('got path request');
    // console.log(req.query);
    // console.log(server_set);
    rfileid = req.query.filename.hashCode();
    redge = req.query.site;
    rsize = parseInt(req.query.filesize);
    rtime = parseInt(req.query.time);
    lf = 3
    path = 'root://';
    if (server_set.has(redge)) {
        l1 = server_set.get(redge);
        s1 = l1.get_server(rfileid);
        found = s1.add_request(rfileid, rsize, rtime);
        l1.requests_received += 1;
        if (found) {
            lf = 0;
            l1.files_delivered += 1;
            l1.data_delivered += rsize;
        }
        path += s1.hostname + '//';

        // if (!s1.upstream_site === null) {
        l2 = server_set.get(l1.upstream_site);
        s2 = l2.get_server(rfileid);
        if (!found) {
            l2.requests_received += 1;
            found = s2.add_request(rfileid, rsize, rtime)
            if (found) {
                lf = 1
                l2.files_delivered += 1;
                l2.data_delivered += rsize;
            }
        }
        path += s2.hostname + '//';

        // if (!s2.upstream_site == null) {
        l3 = server_set.get(l2.upstream_site);
        s3 = l3.get_server(rfileid);
        if (!found) {
            l3.requests_received += 1;
            found = s3.add_request(rfileid, rsize, rtime)
            if (found) {
                lf = 2
                l3.files_delivered += 1;
                l3.data_delivered += rsize;
            }
        }
        path += s3.hostname + '//';
        // }
        // }

        if (nrequests % 10000 == 0) {
            console.log(server_set);
        }
        nrequests += 1

        // console.log(path);
        res.statusCode = 200;
        res.end('lf_' + lf);
    }
    else {
        res.statusCode = 404;
        res.end('No edge server with that name.');
    }
    res.end();
});

app.get('/status', function (req, res) {
    console.log(server_set);
    res.json(JSON.stringify([...server_set]));
});

app.post('/simulate', function (req, res) {
    // console.log(req.body);
    var counts = [0, 0, 0, 0]
    var sizes = [0, 0, 0, 0]
    pt = 0;
    for (var i = 0, len = req.body.length; i < len; i++) {
        rfileid = req.body[i].filename.hashCode();
        redge = req.body[i].site;
        rsize = parseInt(req.body[i].filesize);
        rtime = parseInt(req.body[i].time);

        l1 = server_set.get(redge);
        s1 = l1.get_server(rfileid);
        found = s1.add_request(rfileid, rsize, rtime);
        l1.requests_received += 1;
        if (found) {
            l1.files_delivered += 1;
            l1.data_delivered += rsize;
            counts[0] += 1;
            sizes[0] += rsize;
            continue
        }

        if (l1.upstream_site == 'xc_Origin') {
            counts[3] += 1
            sizes[3] += rsize
            continue
        }

        l2 = server_set.get(l1.upstream_site);
        s2 = l2.get_server(rfileid);
        l2.requests_received += 1;
        found = s2.add_request(rfileid, rsize, rtime)
        if (found) {
            l2.files_delivered += 1;
            l2.data_delivered += rsize;
            counts[1] += 1;
            sizes[1] += rsize;
            continue
        }

        if (l2.upstream_site == 'xc_Origin') {
            counts[3] += 1
            sizes[3] += rsize
            continue
        }

        l3 = server_set.get(l2.upstream_site);
        s3 = l3.get_server(rfileid);
        l3.requests_received += 1;
        found = s3.add_request(rfileid, rsize, rtime)
        if (found) {
            l3.files_delivered += 1;
            l3.data_delivered += rsize;
            counts[2] += 1;
            sizes[2] += rsize;
        }

        counts[3] += 1
        sizes[3] += rsize

    }
    res.json({
        counts: counts,
        sizes: sizes
    })
    // res.end(result.toString());
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
    await es.update_server(req.body);
    await reload_servers();
    res.status(200).send('OK');
});

app.delete('/server/:server_id', async function (req, res) {
    console.log('removing server');
    console.log(req.params.server_id);
    await es.delete_server(req.params.server_id);
    await reload_servers();
    res.status(200).send('OK');
});

app.get('/stress_test/', async function (req, res) {
    console.log('stress file requested');
    sfile = await es.get_stress_file();
    res.json(sfile);
});

app.get('/stress_result/:_id/:status/:rate', function (req, res) {
    console.log('stress result');
    console.log(req.params);
    es.add_stress_result(req.params);
    res.status(200).send('OK');
});


app.get('/wipe', async function (req, res) {
    console.log('WIPING all caches!!!');
    // loop over sites and servers in server_set and wipe them.
    res.status(200).send('OK');
});



// app.use((err, req, res, next) => {
//     console.error('Error in error handler: ', err.message);
//     res.status(err.status).send(err.message);
// });


async function reload_servers() {
    console.log('reloading servers');
    server_set = await es.load_server_tree();
}


var httpsServer = https.createServer(credentials, app).listen(443);

// redirects to https if someone comes on http.
http.createServer(function (req, res) {
    res.writeHead(302, { 'Location': 'https://' + config.SITENAME });
    res.end();
}).listen(80);

// for testing
// var httpsServer = http.createServer(app).listen(80);

async function main() {
    try {
        await reload_servers();
        // console.log("---------------\n", server_set);
    } catch (err) {
        console.error('Error: ', err);
    }
}

main();