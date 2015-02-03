# ski_data

ski_data is a project that provides interactive visualizations on ski area data.

A running instance is hosted at http://levibracken.com/ski.
  
##Running the application

To run locally...

    $ python ski_data.py

You can then access the WebUI at http://localhost:5000.

## Docker

This project can be deployed as a Docker container.

To build a ski_data image...

	$ docker build -t="ski_data" .

To start a ski_data container...

	$ docker run -d -P --name ski_data ski_data