# Social Events API

## Table of contents

-   [About the project](#about-the-project)
-   [Tech Stack](#tech-stack)
-   [Features](#features)
-   [Dependency management](#dependency-management)
-   [Dependencies](#dependencies)
-   [Setup](#setup)

## About the project

Social Events API is a backend application that allows users to create and manage events for their group of friends. The API endpoints can be used with a matching frontend or accessed through an HTTP client (e.g. curl, Postman).

<p align="right">(<a href="#top">back to top</a>)</p>

## Features

-   User authentication: All users must be authenticated in order to use the application.
-   User management: Users can create groups, invite friends, and manage their own personal events.
-   Group management: Groups have an admin who can create and manage events, invite friends to join the group, and remove members from the group.
-   Event management: Users can create, edit, and delete events. Events can be set as recurring events or one-time events.
-   Mailing list: Users can invite friends to events by sending emails from the application.
-   Message box: Users can send private messages to other users or start thread messages for group discussions.
-   Location management: Users can add locations for events.

<p align="right">(<a href="#top">back to top</a>)</p>

## Tech stack

-   Django
-   Django Rest Framework
-   PostgreSQL
-   Celery
-   Redis
-   Docker and Docker Compose
<p align="right">(<a href="#top">back to top</a>)</p>

## Dependency management

-   poetry
<p align="right">(<a href="#top">back to top</a>)</p>

## Dependencies

-   Python ^3.10
-   Django ^4.1.5
-   Django REST framework ^3.14.0
-   Django Debug Toolbar ^3.8.1
-   Celery ^5.2.7
-   dj-database-url ^1.2.0
-   Psycopg2 ^2.9.5
-   Pillow ^9.4.0
-   Django Recurrence ^1.11.1
-   Django Light ^0.1.0.post3
-   Django Filter ^22.1
-   dj-rest-auth ^3.0.0
-   Django Allauth ^0.52.0
-   Django REST framework Simple JWT ^5.2.2
-   drf-spectacular ^0.26.0

<p align="right">(<a href="#top">back to top</a>)</p>

## Setup

To run the project you need `Docker` and `Docker Compose` on your machine.

Open your terminal and type in required commands:

```
$ git clone git@github.com:lolekgk/social-events-api.git
$ cd social-events-api
```

Fill in provided `.env.sample` file with the required values and save as `.env`.

```
$ docker-compose build
$ docker-compose up
$ docker exec -it social_events bash
```

Visit [localhost:8000/redocs/](http://localhost:8000/redocs/) in the browser to see all available endpoints and their details.

<p align="right">(<a href="#top">back to top</a>)</p>
