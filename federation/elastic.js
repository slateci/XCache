var elasticsearch = require('elasticsearch');
const server = require('./server.js');
const site = require('./site.js');

// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests",
    STRESS_INDEX: "stress",
    SIMULATION: true
};


module.exports = class Elastic {

    constructor() {
        this.es = new elasticsearch.Client({ host: config.ELASTIC_HOST, log: 'error' });
        this.requests = [];
        this.stress_requests = [];
        this.stress_results = [];
    }

    async add_request(request) {
        console.log("Adding request to ES ...");
        this.requests.push(request);
        if (this.requests.length > 1) {
            this.save_requests(this.requests);
            this.requests = [];
        }
    };

    async save_requests(requests) {
        console.log("saving requests to ES...");
        var docs = { body: [] }
        for (var i = 0, len = requests.length; i < len; i++) {
            docs.body.push({ index: { _index: config.REQUESTS_INDEX, _type: 'docs' } })
            docs.body.push(requests[i]);
        }
        try {
            await this.es.bulk(docs);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async delete_server(server_id) {
        console.log("deleting server from ES...");
        try {
            const response = await this.es.deleteByQuery({
                index: config.SERVERS_INDEX, type: 'docs', refresh: true,
                body: { query: { match: { "_id": server_id } } }
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async add_server(server) {
        console.log("Adding server to ES...");
        server.created = new Date().getTime();
        server.last_update = new Date().getTime();
        delete server.files;
        delete server.current_utilization;
        console.log(server);
        try {
            const response = await this.es.index({
                index: config.SERVERS_INDEX, type: 'docs', refresh: true,
                id: server.id,
                body: server
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async update_server(server) {
        console.log("Updating server info in ES...");
        try {
            const response = await this.es.update({
                index: config.SERVERS_INDEX, type: 'docs', id: server.site + '_' + server.index.toString(),
                refresh: true,
                body: {
                    doc: {
                        "serves": server.serves,
                        "upstream_site": server.upstream_site,
                        "upstream_fallback": server.upstream_fallback,
                        "hostname": server.hostname,
                        "capacity": server.capacity,
                        "status": server.status,
                        "last_update": new Date().getTime()
                    }
                }
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async load_server_tree() {
        // console.log("loading all server info...");
        var server_tree = new Map();
        try {
            const response = await this.es.search({
                index: config.SERVERS_INDEX, type: 'docs',
                body: {
                    size: 200,
                    query: { bool: { must: [{ match: { status: "active" } }] } }
                }
            });
            // console.log(response);
            if (response.hits.total == 0) {
                console.log("No active servers found.");
                return false;
            }
            else {
                console.log("Active servers found.");
                for (var i = 0; i < response.hits.hits.length; i++) {
                    var si = response.hits.hits[i]._source;
                    var ser = new server();
                    ser.initialize(si);
                    if (!server_tree.has(ser.site)) {
                        server_tree.set(ser.site, new site(ser.site));
                    }
                    var os = server_tree.get(ser.site);
                    os.add_server(ser);
                    // server_tree.set(ser.site, os);
                }
            };
        } catch (err) {
            console.error(err)
        }
        console.log('Done.');
        return server_tree;
    };

    async get_stress_file() {
        if (this.stress_requests.length == 0) {
            await this.load_stress_files();
        }
        var sf = this.stress_requests.shift();
        this.update_stress_file(sf, 'processing');
        return sf;
    }

    async load_stress_files(nfiles = 50) {
        console.log("loading batch of stress paths ...");
        try {
            const response = await this.es.search({
                index: config.STRESS_INDEX, type: 'docs',
                body: {
                    size: nfiles,
                    query: { bool: { must: [{ match: { status: "in queue" } }] } },
                    sort: [{ timestamp: { order: "asc" } }]
                }
            });
            // console.log(response);
            if (response.hits.total == 0) {
                console.log("No files in queued");
                return false;
            }
            else {
                console.log("Files found.");
                for (var i = 0; i < response.hits.hits.length; i++) {
                    var si = response.hits.hits[i]._source;
                    // console.log(si);
                    var tf = si;
                    tf['_id'] = response.hits.hits[i]._id;
                    this.stress_requests.push(tf);
                }
            };
        } catch (err) {
            console.error(err)
        }
        console.log('Done.');
    };

    add_stress_result(result) {
        this.stress_results.push(result);
        if (this.stress_results.length > 1) {
            this.save_stress_results(this.stress_results);
            this.stress_results = [];
        }
    };

    async update_stress_file(sf, newstatus) {
        // console.log("updating stress file:", sf);
        this.es.update({
            index: config.STRESS_INDEX, type: 'docs', id: sf._id,
            body: { doc: { status: newstatus, updated_at: new Date().getTime() } }
        });
    };

    async save_stress_results() {
        console.log("saving stress results...");

        var docs = { body: [] }
        for (var i = 0, len = this.stress_results.length; i < len; i++) {
            var res = this.stress_results.pop();
            docs.body.push({ update: { _index: config.STRESS_INDEX, _type: 'docs', _id: res._id } });
            docs.body.push({ doc: { rate: res.rate, status: res.status, updated_at: new Date().getTime() } });
        }
        try {
            await this.es.bulk(docs);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

}



