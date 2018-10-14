
// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests",
    SIMULATION: true
};

module.exports = class Server {

    // constructor(site, upstream_site, hostname, capacity, index) {
    initialize(params) {
        // console.log(params)
        if (!(params.hasOwnProperty('site') &&
            params.hasOwnProperty('upstream_site') &&
            params.hasOwnProperty('index') &&
            params.hasOwnProperty('hostname') &&
            params.hasOwnProperty('capacity'))) {
            return false;
        }

        this.site = params.site;
        this.upstream_site = params.upstream_site;
        this.index = params.index;
        this.hostname = params.hostname;
        this.capacity = params.capacity;
        this.id = params.site + '_' + params.index;

        this.status = 'disabled';
        this.lwm = 0.85;
        this.hwm = 0.95;

        if (params.hasOwnProperty('status')) { this.status = params.status; }
        if (params.hasOwnProperty('lwm')) { this.lwm = params.lwm; }
        if (params.hasOwnProperty('hwm')) { this.hwm = params.hwm; }
        if (params.hasOwnProperty('lat')) { this.lat = params.lat; }
        if (params.hasOwnProperty('long')) { this.long = params.long; }
        if (params.hasOwnProperty('upstream_fallback')) { this.upstream_fallback = params.upstream_fallback; }
        if (params.hasOwnProperty('created')) { this.created = params.created; }
        if (params.hasOwnProperty('last_update')) { this.last_update = params.last_update; }

        this.wipe();

        return true;
    }

    set_status(status) {
        this.status = status;
    }
    set_limits(lwm, hwm) {
        this.lwm = lwm;
        this.hwm = hwm;
    }
    set_location(lat, long) {
        this.lat = lat;
        this.long = long;
    }
    set_fallback(fallback) {
        this.upstream_fallback = fallback;
    }

    wipe() {
        if (config.SIMULATION == true) {
            this.files = new Map();
            this.current_utilization = 0;
        }
    }

    cleanup() {
        console.log('starting cleanup.')
        // LRU
        var n = Array.from(this.files);
        // sort array in increasing last access time order.
        n.sort(function (a, b) { return a[1][2] - b[1][2]; });
        var i = 0;
        while (this.current_utilization > this.capacity * this.lwm) {
            this.files.delete(n[i][0]);
            this.current_utilization -= n[i][1][0];
        }
    }

    add_request(filehash, filesize, access_time) {
        if (!this.files.has(filehash)) {
            this.files.set(filehash, [filesize, 1, access_time]);
            this.current_utilization += filesize;
            if (this.current_utilization > this.capacity * this.hwm) {
                console.log(filesize, this.current_utilization);
                console.log(this.capacity, this.hwm);
                this.cleanup();
            }
            return false;
        }
        else {
            var v = this.files.get(filehash);
            v[1] += 1;
            v[2] = access_time;
            this.files.set(filehash, v);
            return true;
        }
    };

}