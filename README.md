# Tiny Organic

This repository contains the code necessary for the new and improved tinyorganics.com site. The instructions below are subject to change as the codebase and the team grows.

### Codebase organization

Our codebase leverages Docker/Docker Compose to easily spin up a development environment on a developer's machine.

#### Stack
 - Backend -> Python/Django
    - Testing -> Django Test
 - Frontend -> React/Redux/Typescript
    - Testing -> Jest/Enzyme
 - Ops -> Docker/k8s
 - Database -> Postgres
 - Cache -> Redis
 - Message Queue -> Celery
 - Message Broker -> RabbitMQ
 - CI -> Github Actions

#### Directories
At the base of the repo, you'll currently find the following directories:

* `backend` - contains all of our backend application code. This part of the codebase is written in `Python` using the `Django` web framework.
* `envs` - this is where all the files containing environment variables will go. For best practices, it's best to not store credentials (such as API keys) in plaintext, even if this is a private repository. We will be leveraging an ecryption tool to encrypt the files within this directory.
* `frontend` - contains the code for the frontend component of the platform. It currently uses TypeScript/React
* `services` - contains the Docker files and configurations for the container services we're to spin up locally.

### Getting Started

You'll need to download & install a few tools before you can begin to code.

1. XCode developer tools
2. [Homebrew](https://brew.sh/)
3. [iTerm](https://iterm2.com/downloads.html) (optional) 
4. [Docker for Mac](https://docs.docker.com/desktop/mac/install/)
5. [Node.js](https://nodejs.org/en/)

#### Spinning up your local environment
1. create an SSH key `ssh-keygen` (go through the steps, no passphrase, no name)
2. upload that SSH key to your github profile on [github.com](github.com)
3. clone the repository `git clone git@github.com:tiny-organics/tinydotcom.git`
4. change directory into your local repository `cd tinydotcom`
5. use docker compose to spin up your local environment `docker-compose up --build`

It will take a couple of minutes to spin up your local environment on the first run. We try to leverage as much of Docker's caching to speed things up over continuous builds.

#### After spinning up

You'll need to do a few things such as setup the superuser, bundle Django's static assets together, etc. Luckily, there are some django commands that make all of this easy. Run the following commands:

1. `docker-compose exec backend bash` - this logs you into the backend container
2. `cd backend` - this puts you in the backend directory once inside the container
2. `django-admin migrate` - this will run existing database migrations once you're inside the backend container
3. `django-admin collectstatic --noinput` - this will bundle static assets on the backend. This powers the homepage.
4. `python manage.py seed_initial_data` - this will create the superuser and the minimal data required to run.

Once you're done, you can access `localhost:8000` in your browser. To begin development for the React part of the stack, just change the code in the `frontend` directory. Webpack is configured to bundle and write to a common `static` directory in the `backend` directory. To preview your React app changes head over to `localhost:8000/onboarding/`. 


#### Sync product data
1. Navigate to `localhost:8000/admin/`
2. Login with the superuser credentials email=`superuser@tinyorganics.com` and password=`tinythoughtproperty1`
3. Go to `Products` and click the button that says, sync products from Shopify. This will pull in data from our test shopify store. This is also how we manage displaying certain products in our recipe page.

<img width="1501" alt="Screen Shot 2022-03-31 at 12 55 37 PM" src="https://user-images.githubusercontent.com/87022787/161109339-52c6acb9-12cd-49bb-b977-bd3f54efe0e8.png">



#### After data is set up
In an incognito window, you should now be ready to go through the onboarding and checkout flow. When you enter the credit card credentials, you may use Stripe's test cards:

Card Number: `4242 4242 4242 4242`
Expiration Date: any date in the future
Zipcode: any 5 digit number
