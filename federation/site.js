
// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests",
    SIMULATION: true
};

module.exports = class Site {

    constructor(name) {
        this.name = name;
        this.requests_received = 0;
        if (config.SIMULATION == true) {
            this.files_delivered = 0;
            this.data_delivered = 0;
        }
        this.capacity = 0;
        this.servers = [];
    }

    set_fallback(fallback) {
        this.upstream_fallback = fallback;
    }

    add_server(server) {
        this.servers.push(server);
        this.capacity += server.capacity * server.hwm;
        this.upstream_site = server.upstream_site;
    }

    // returns server id and hostname to be asked for the file. 
    get_server(fileid) {
        return this.servers[fileid % this.servers.length];
    }
}