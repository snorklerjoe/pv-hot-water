# A Plan for the Container Healthchecks

This is for the purpose of planning ahead in the priority of stability and reliability.

Each container should have a health monitor. This should schedule a task to periodically log health in the database and delete entries older than a configured amount.  
The api and/or web app should be able to then obtain this information (so it can be displayed on a dashboard or something).

There should be a config-configurable command line utility to access & process these healthchecks, used by docker to determine whether or not to restart the container.

## Things to store in healthchecks

- Time
- Uptime of the container
- Set of named uptimes for different sub threads
- Alarm / Critical state (boolean flag)
- General health
