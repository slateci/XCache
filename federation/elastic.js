var elasticsearch = require('elasticsearch');

// var config = require('/etc/backend-conf/config.json');
var config = {
    "SITENAME": "xcache.org",
    "ELASTIC_HOST": "atlas-kibana.mwt2.org:9200"
};


module.exports = class Elastic {

    constructor() {
        this.es = new elasticsearch.Client({ host: config.ELASTIC_HOST, log: 'error' });
    }

    async write() {
        console.log("adding user to ES...");
        try {
            const response = await this.es.index({
                index: 'mlfront_users', type: 'docs', id: this.id,
                refresh: true,
                body: {
                    "username": this.username,
                    "affiliation": this.affiliation,
                    "user": this.name,
                    "email": this.email,
                    "event": config.NAMESPACE,
                    "created_at": new Date().getTime(),
                    "approved": this.approved,
                    "approved_on": this.approved_on
                }
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async delete() {
        console.log("deleting user from ES...");
        try {
            const response = await this.es.deleteByQuery({
                index: 'mlfront_users', type: 'docs',
                body: { query: { match: { "_id": this.id } } }
            });
            console.log(response);
        } catch (err) {
            console.error(err)
        }
        console.log("Done.");
    };

    async update() {
        console.log("Updating user info in ES...");
        try {
            const response = await this.es.update({
                index: 'mlfront_users', type: 'docs', id: this.id,
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

    async load() {
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



