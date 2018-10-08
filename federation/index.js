var express = require('express');
var https = require('https');
var http = require('http');

const elastic = require('./elastic.js');

// var config = require('/etc/backend-conf/config.json');
var config = {
    "SITENAME": "xcache.org",
    "ELASTIC_HOST": "atlas-kibana.mwt2.org:9200"
};

console.log('XCache backend server starting ... ');


const app = express();

app.use(express.static('public'));

function save_requests() {
    const es = new Elastic();

}

app.get('/path', function (req, res) {
    console.log('getting path');
    console.log(req);
    link = 'xxx/xxx/xxx/asdf.root';
    res.status(200).send(link);

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
