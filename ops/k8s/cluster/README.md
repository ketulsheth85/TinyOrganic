# K8s Cluster and Application Setup

To deploy our application, we leverage Amazon's Elastic Kubernetes Service (EKS) running on Fargate.
Fargate leverages Amazon's serverless infrastructure to run code in. Running EKS on Fargate gives us
the advantage of not having to worry about auto-scaling machines, choosing running OSs, etc. AWS will
handle all of that for us. All we have to do is focus on building our application, and deploying it.


### File Structure
The directory structure of this directory:

```
ops/k8s
│   README.md
└───app
│   └───base
|   └───demo
|   └───staging
|   └───production
└───cluster
    └─── base
    └─── demo
    └─── staging
    └─── production
```

**apps** - This directory contains all of the Kubernetes (K8s) configurations to run the app in a specific environment.

**cluster** - This directory contains all of the Kubernetes (K8s) configurations to manage the cluster.

### eksctl
To create and manage the EKS clusters, you'll have to download and install [eksctl](https://eksctl.io/introduction/#installation).

### Running EKS on Fargate

Before being able to run and access the clusters and the K8s components in the cloud, you'll need an AWS account.

1. You'll also need to install the [aws-iam-authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html).
2. Checkout the documentation on configuring access to the clusters. [Click Here](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/)
3. After following the steps, you should be ready to access the clusters on EKS.

#### Helpful Commands
As mentioned previously, EKS on Fargate allows us to run a "serverless" infrastructure. This means AWS will handle all the
provisioning of properly sized servers for the workloads we run, they'll choose the OS and auto-scale our infrastructure.

Fargate doesn't support SSH access into the nodes just yet. While we may not have access to these nodes directly, K8s
gives us a few commands to troubleshoot the nodes, pods, and other k8s components.

##### List Running Pods
`kubectl get pods -n <namespace>`

##### List Services
`kubectl get svc -n <namespace>`

##### View Pod Logs
`kubectl logs -n <namespace> <pod-name>`

There are plenty of more commands we can leverage to gain further insight into what is going on "underneath the hood" in
our infrastructure. [Click Here](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) to see the cheatsheet. If you
don't have `kubectl` installed, [Click Here Instead](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

##### Useful Kubectl Accessories
Often, you'll find yourself having to switch k8s "contexts". These are just having to manually re-configure your kubeconfig
to tell kubectl which namespace, or environment (staging, prod) you'd like to execute a given command on. This can get quite
confusing and cumbersome to do.

[Kubens](https://github.com/ahmetb/kubectx) gives you a more convenient and faster way to switch between k8s environments
and namespaces.

To learn more about how to run a K8s application on Fargate click [Here](https://www.learnaws.org/2019/12/16/running-eks-on-aws-fargate/).

### Deploying to an environment

1. Make sure you're in the right environment
`kubectx <environment-id>`
2. Deploy changes
    * Use kustomize to re-deploy new changes
`kustomize build --load-restrictor LoadRestrictionsNone ops/k8s/app/<environment-name> | kubectl apply -f -`
    * Use kubectl to restart a deploy
`kubectl restart rollout restart <"all" or deployment-name>`
3. Track the status of your deploy
`watch kubectl get pods`.

Note: If you do not see any pods when running the `kubectl` command, you might not be in the right namespace. To fix that,
run `watch kubectl get pods -n <namespace>` or switch to the namespace `kubens <namespace>` then run the previous `kubectl`
command.

4. You'll want to make sure that the alb exists when spinning up a new cluster. Run `kubectl describe ing -n staging`
