Setting Up a Node.js Express Application with Docker

This guide will help you set up a Node.js Express application with MongoDB using Mongoose, along with Docker configuration for remote access.

Initialize Node.js Project

Initialize npm Project

    npm init -y

Install Dependencies

    npm install express nodemon mongoose dotenv cors body-parser dockerode

Install nodemon globally (if not already installed):

    npm install -g nodemon

Configuring Docker for Remote Access

Use the command below to open an override file for docker.service in a text editor.

    sudo systemctl edit docker.service

Add Remote Access Configuration

Add or modify the following lines in the editor, replacing with your desired values:

        [Service]
        ExecStart=
        ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375

Save the file and reload the systemctl configuration.

    sudo systemctl daemon-reload

Restart Docker to apply the changes.

    sudo systemctl restart docker.service

Verify Docker Configuration
Check if Docker is now listening on the configured port (2375).

    sudo netstat -lntp | grep dockerd

You should see an output like:

    tcp        0      0 0.0.0.0:2375          0.0.0.0:*               LISTEN      <dockerd_pid>/dockerd

Running the Node.js Express Application

Now, you can start building your Node.js Express application using the installed dependencies. Use nodemon to automatically restart the server when changes are made to your code.

    nodemon

That's it! You've set up a Node.js Express application with Docker configured for remote access. Happy coding! 🚀
