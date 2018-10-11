var elasticsearch = require('elasticsearch');
const server = require('./server.js');
const site = require('./site.js');

// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests",
    SIMULATION: true
};


module.exports = class Elastic {

    constructor() {
        this.es = new elasticsearch.Client({ host: config.ELASTIC_HOST, log: 'error' });
    }

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

}



