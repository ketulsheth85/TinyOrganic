# DevOps

### Getting Started

To get setup with deploying from your machine, you'll need to set a few things
up. Before beginning, you'll need to obtain an AWS new user credential file. Reach out
to the AWS admin to get one.

1. Download the [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
2. Configure the `aws-cli` by running `aws configure` once downloaded
   1. enter your aws access key
   2. enter your aws secret key
   3. the aws region is `us-east-1`
   4. set the default output to `json`
3. Note that your local aws profile is called `default`.

At this point you are now ready to provision/destroy aws resources (RBAC permitting of course)

### Application Infrastructure Components

Our application runs on AWS using various Amazon services such as,

* EKS - Elastic Kubernetes Service. We use Kubernetes to deploy and orchestrate the application
* ECR - Elastic Container Registry. We containerize our application
* RDS - Relational Database Service. 
* Elasticache - We use this to spin up a Redis instance
* AmazonMQ - We leverage RabbitMQ as our task queue message broker for asynchronous tasks
* AWS Cloudfront - CDN

In this guide, we'll walk through the steps needed in order to get setup in managing our EKS clusters
in the staging and production environments.

#### ECR

Since our application is containerized, we should begin by building each of our images into 
containers that we package and store in our private container registry, ECR. The services we 
currently containerize are:

* tinydotcom-backend: This image contains the backend business logic and runs on Python 3.9 
& The Django Web framework
* tinydotcom-backend-staging: This is the same image but we use this to deploy to the staging cluster

### eksctl
To create and manage the EKS clusters, you'll have to download and install [eksctl](https://eksctl.io/introduction/#installation).

### Kustomize

Kustomize is a nifty tool that allows us to write clean templated k8s config files. Using basic K8s constructs, you can
build reusable modules to deploy and modify your k8s clusters and environments.

To learn more about Kustomize [Click Here](https://github.com/kubernetes-sigs/kustomize).

##### Useful Kubectl Accessories
Often, you'll find yourself having to switch k8s "contexts". These are just having to manually re-configure your kubeconfig
to tell kubectl which namespace, or environment (staging, prod) you'd like to execute a given command on. This can get quite
confusing and cumbersome to do.

[Kubens](https://github.com/ahmetb/kubectx) gives you a more convenient and faster way to switch between k8s environments
and namespaces.

To learn more about how to run a K8s application on Fargate click [Here](https://www.learnaws.org/2019/12/16/running-eks-on-aws-fargate/).

##### Building and Storing image container (manually)
To build and store the latest container manually, you'll want to take the following steps:
1. In your terminal window, make sure you're inside the repository directory 
and run, `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <replace-with-aws-account-id-here>.dkr.ecr.us-east-1.amazonaws.com`,
If everything was successful, you should see a `Login Succeeded` message as a response.
2. You'll want to build the container, `docker build -t tinydotcom-backend --target production .`
3. After the image is done building, you must tag it with a unique tag. Usually, we tag it with the git revision number.
However, every new push to the ECR should have the `latest` tag associated with it. Run,
`docker tag tinydotcom-backend:latest <replace-with-aws-account-id-here>.dkr.ecr.us-east-1.amazonaws.com/tinydotcom-backend:latest`
4. Now you should be able to push with `docker push <replace-with-aws-account-id-here>.dkr.ecr.us-east-1.amazonaws.com/tinydotcom-backend:latest`
5. Once the push to the ECR service is completed, you can check to see your tag in the AWS ECR dashboard.

##### Building and Pushing image containers (automatically)
There is a build script that does the following:

1. Compiles the react/typescript code to ES5 JS and syncs it to our aws s3 bucket.
This will allow our CloudFront distribution to pull from it and cache it for client use.
2. Builds a docker image of the Dockerfile for our specific docker stages such as `backend`, `celery`, `celerybeat`, `etc`
3. Pushes the images to the appropriate ECR repositories.

Before being able to run this script, you'll need to install and configure certain tools locally. If you've installed these tools,
feel free to skip.
* [`aws-cli`](https://formulae.brew.sh/formula/awscli) - The command line tool for interacting with AWS
* [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#install-with-homebrew-on-macos)

Next, you'll have to configure your aws cli to match your AWS iAM credentials. You can configure
by running `aws configure`. You should receive a prompt asking you for certain credentials, aws-region, and which format 
you'd like to display output from AWS responses.

If you do not have your AWS credentials, contact the AWS admin.

##### Deploying
Deployments can happen in two different ways:

1. Use `kustomize` to build a deployment yaml file in real time and apply it to the cluster/namespace
2. Using `kubectl rollout restart deployment` to restart the EKS pods which are defined in the `deployment.yaml` file

Each way has its particular use-case.

If we make any changes to the environment variables in the .env file which corresponds to an environment, we run the build script,
and then run `kustomize build --load-restrictor LoadRestrictionsNone ops/k8s/app/<environment-name> | kubectl apply -f`.
If you're unsure about what exactly will be applied, run the first command (before the `|`) alone to see what the `kustomize`
command builds before applying it to the cluster.

In the case where we are making codebase changes, such as adding new features, cleaning up code that do not require environment
variables to run, then you use `kubectl rollout restart deployment`. This will restart the pods that belong to the respective deployment.

##### Rolling Back/Deploying specific tags
Our ECR repositories have images that are tagged with the `latest` tag after each build before we officially deploy the new 
images. However, this can place one in a difficult position with rollbacks. Thus, tagging our images with a $GIT_SHA before each
build push is necessary. In the event that a rollback is required, we'll want to do the following:

1. Login to the AWS ECR repository of choice.
2. Look up the desired image/tag
3. Copy the tag id
4. Paste the tag id to the `deployment.patch.yaml` file located in `ops/k8s/app/<environment>`. You'll see
we specify the image registry, repository and the tag. Replace the `latest` with the specific tag id.

In this case, you'll want to run the `kustomize` command since a `kubectl rollout restart deployment` will only restart the 
pods with the same image configurations and will not cause EKS to pull your specified image tag.
