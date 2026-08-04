# Module 13 Reflection

In this module, I learned how login and registration work beyond just saving a user in the database. Before this, my project already had user models, password hashing, and calculation routes, but Module 13 connected those pieces to a real authentication flow. Creating JWT tokens helped me understand how an API can return proof that a user logged in successfully without sending the password back or storing it in plain text.

The front-end part also made the project feel more complete. I created basic register and login pages, added JavaScript validation for email format and password length, and displayed success or error messages based on the server response. This helped me see how the browser and FastAPI communicate through JSON requests.

Testing was one of the most important parts of this module. Unit and integration tests checked the backend logic, while Playwright tested the pages like a real user would. The positive tests confirmed that registration and login worked, and the negative tests checked things like short passwords and wrong login credentials. Running these tests through GitHub Actions made the workflow more reliable because every push checks the code automatically before the Docker image is pushed to Docker Hub.

One challenge was keeping the JWT routes, database logic, and front-end validation consistent. I overcame it by testing one small part at a time and using the earlier modules as a guide. I still want to get better at authentication and token security because this is a big part of real web applications.
