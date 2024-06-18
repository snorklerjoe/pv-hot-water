<!-- markdownlint-disable-file MD007 -->
# Primary TODOs

This document is a basic plan of attack for this project.  
The purpose of this document is really just for my own organization.

## Tasks

- [x] Establish basic directory structure
- [ ] Build dev/prod workflow and create boilerplate code
    - [ ] Create webapp boilerplate
    - [ ] Establish a dev workflow (with a dev sqlite database)
    - [ ] Write `Dockerfile`s
    - [ ] Write the `docker-compose.yaml` file
    - [ ] Establish production build workflow
- [ ] Create basic database models
- [ ] Establish daemon structure (threads, socket, etc)
- [ ] Set up communication between the api and daemon (UNIX socket?) & create minimal api endpoint
- [ ] Create docker healthchecks (*especially for daemon*)
