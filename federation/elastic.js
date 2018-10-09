var elasticsearch = require('elasticsearch');

// var config = require('/etc/backend-conf/config.json');
var config = {
    SITENAME: "xcache.org",
    ELASTIC_HOST: "atlas-kibana.mwt2.org:9200",
    SERVERS_INDEX: "xc_servers",
    REQUESTS_INDEX: "xc_requests"
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
                index: config.SERVERS_INDEX, type: 'docs',
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
        console.log(server);
        try {
            const response = await this.es.index({
                index: config.SERVERS_INDEX, type: 'docs',
                id: server.site + '_' + server.index.toString(),
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
                body: {
                    doc: {
                        "approved_on": this.approved_on,
                        "approved": this.approved
                    }
                }
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async load_tree() {
        console.log("getting user's info...");

        try {
            const response = await this.es.search({
                index: 'mlfront_users', type: 'docs',
                body: {
                    query: {
                        bool: {
                            must: [
                                { match: { event: config.NAMESPACE } },
                                { match: { _id: this.id } }
                            ]
                        }
                    }
                }
            });
            // console.log(response);
            if (response.hits.total == 0) {
                console.log("user not found.");
                return false;
            }
            else {
                console.log("User found.");
                var obj = response.hits.hits[0]._source;
                // console.log(obj);
                // var created_at = new Date(obj.created_at).toUTCString();
                // var approved_on = new Date(obj.approved_on).toUTCString();
                this.name = obj.user;
                this.email = obj.email;
                this.affiliation = obj.affiliation;
                this.created_at = obj.created_at;
                this.approved = obj.approved;
                this.approved_on = obj.approved_on;
                return true;
            };
        } catch (err) {
            console.error(err)
        }
        console.log('Done.');
        return false;
    };

    async add_service(service) {
        try {
            service.owner = this.id;
            service.timestamp = new Date().getTime();
            service.user = this.name;
            console.log('creating service in es: ', service);
            await this.es.index({
                index: 'ml_front', type: 'docs', body: service
            }, function (err, resp, status) {
                console.log("from ES indexer:", resp);
            });
        } catch (err) {
            console.error(err)
        }
    };

}



