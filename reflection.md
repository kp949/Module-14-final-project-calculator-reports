# Final Project Reflection

For this final project, I learned how to bring together the work from the previous modules into one more complete application. In the first few modules of the course, I had created user models, hashed passwords, implemented JWT login, created a number of calculation routes, and even implemented BREAD functions for working with the data in a number of models. For the final portion of the course, I decided to add a reports page for logged-in users that would summarize their saved calculations.

Connecting backend to frontend. My reports page simply takes all the calculation records for a logged-in user and organizes them into a meaningful summary (i.e. total, operation count, average, highest and lowest) and also lists out their most recent calculations. I can now finally see how an app can do more than just store data, actually organize that data and make it useful for the user.

In addition to the core work for this project, I tested various aspects of the application. This work involved writing unit tests, and then subsequent integration tests. Later I used Playwright to perform end-to-end tests. GitHub Actions were able to automatically test and build the Docker image after each push of work to the GitHub repository.

One thing I would like to improve on is how we do authentication, better reports for the user as well as making the front end cleaner for improved users experience.
