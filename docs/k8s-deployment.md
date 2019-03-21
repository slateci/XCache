Kubernetes v1.10 on CentOS 7
------------------------------
# Head node installation
On the head node, install Docker CE and Kubernetes:
```
# yum update -y
# yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# yum install docker-ce docker-ce-cli containerd.io -y
# systemctl enable --now docker 
# cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
# setenforce 0
# yum install -y kubelet kubeadm kubectl
# systemctl enable --now kubelet
```

At this point, docker should be running and the kubelet should be crash looping. if Docker won't start and complains about overlayfs, make sure you've updated and reboot into the latest kernel. 

If you have swap, you'll need to disable it:
```
swapoff -a
sed -e '/swap/s/^/#/g' -i /etc/fstab
```

Now start kubeadm
```
# kubeadm init
```

Once it's done, you should see:

```
Your Kubernetes master has initialized successfully!
```

Follow the instructions from the shell output. *most importantly*, save the `kubeadm join ...`  line as it has an important token in it. This is needed to join additional nodes to the cluster. 

Add Calico networking (there are many possible plugins, we've chosen this one based on best practices)
```
# kubectl apply -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/rbac-kdd.yaml
# kubectl apply -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calico-networking/1.7/calico.yaml
```

Check to see that the Master is ready
```
$ kubectl get nodes
NAME                STATUS    ROLES     AGE       VERSION
k8s-head.mwt2.org   Ready     master    1h        v1.13.0

```

Create a .kube/config for a regular user:
```bash
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### Optional - Enabling the Kubernetes dashboard
```
$ kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
secret "kubernetes-dashboard-certs" created
serviceaccount "kubernetes-dashboard" created
role.rbac.authorization.k8s.io "kubernetes-dashboard-minimal" created
rolebinding.rbac.authorization.k8s.io "kubernetes-dashboard-minimal" created
deployment.apps "kubernetes-dashboard" created
service "kubernetes-dashboard" created
```

To access the dashboard, you'll want to have your `.kube/config` and  `kubectl` on your workstation/laptop and run
```
kubectl proxy
```

Then you can access the dashboard at `http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/`

It may display errors about not being able to work in the default namespace. If so, you'll need to do the following:
```bash
kubectl create serviceaccount dashboard -n default
kubectl create clusterrolebinding dashboard-admin -n default --clusterrole=cluster-admin --serviceaccount=default:dashboard
```

Then, to get the token for authentication:
```
kubectl get secret $(./kubectl get serviceaccount dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode
```


### Allow jobs to run on the head node 
By default, the master has a "taint" that does not allow pods to be scheduled to it. For single node clusters, it is highly recommended to remove this taint so pods may be launched:
```
kubectl taint nodes --all node-role.kubernetes.io/master-
```

# Adding Workers
Hopefully you saved the output of `kubeadm init`. If so, you can just copy/paste the `kubeadm join ...` bits from the output into your worker node.

If not, here's how to regenerate it. On the master:
```
$ sudo kubeadm token create --print-join-command
```

And then to join the cluster from a worker:
```
kubeadm join <master ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

Just paste that into your worker. *Note that the token expires after 24h, after which you'll need to create a new token to add workers to your cluster*. 

# Installing SLATE
Add the SLATE repository and install the client:
```
cat << EOF > /etc/yum.repos.d/slate.repo
[slate-client]
name=SLATE-client
baseurl=https://jenkins.slateci.io/artifacts/client/
enabled=1
gpgcheck=0
repo_gpgcheck=0
EOF

yum install slate-client -y
```

Go to the SLATE portal - https://portal.slateci.io and go to the "CLI Access" page to get your SLATE token. Run the script there to install your token to `~/.slate/token`.  Once completed, you can register your cluster with SLATE:
```
slate cluster create <clustername> --group <somegroupname> --org "Some Org Name" 
```
