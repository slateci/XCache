XCache is a service that provides caching of data accessed using [xrootd protocol](http://xrootd.org/). It sits in between client and an upstream xrootd servers and can cache/prefetch full files or only blocks already requested. 

To run this chart one needs a k8s cluster with a node labeled: __xcache-capable: "true"__. This node will have at least 10Gbps connection and at least few TB local disk (preferably mounted at __/scratch__).

To set it up one needs to change values in values.yaml:
*   externalIPs
* 

