Kubernetes v1.10 on CentOS 7
------------------------------
# Head node installation
On the head node:
```
# yum update -y
# yum install -y docker
# systemctl enable docker && systemctl start docker
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
# systemctl enable kubelet && systemctl start kubelet
```

At this point, docker should be running and the kubelet should be crash looping. if Docker won't start and complains about overlayfs, make sure you've updated and reboot into the latest kernel. 

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
# kubectl apply -f https://docs.projectcalico.org/v3.0/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml
```

Check to see that the Master is ready
```
$ kubectl get nodes
NAME                STATUS    ROLES     AGE       VERSION
k8s-head.mwt2.org   Ready     master    1h        v1.10.0

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


### Optional - Allow workers to run on head node
You can now add additional nodes to the cluster, or "taint" the master to allow work to be scheduled onto it (single node configuration)
```
kubectl taint nodes --all node-role.kubernetes.io/master-
```

# Adding Workers
Hopefully you saved the output of `kubeadm init`. If so, you can just copy/paste the `kubeadm join ...` bits from the output into your worker node.

If not, here's how to regenerate it. On the master:
```
$ sudo kubeadm token create --print-join-command
kubeadm join <master ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

Just paste that into your worker. *Note that the token expires after 24h, after which you'll need to create a new token to add workers to your cluster*. 



------

# Adding Users and RBAC
