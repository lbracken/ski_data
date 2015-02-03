# Builds a Docker image to run ski_data with uWSGI application server
FROM lbracken/flask-uwsgi
MAINTAINER Levi Bracken <levi.bracken@gmail.com>

# Create a symlink with a unique name to static resources.  This volume can
# then get mounted by an nginx container to directly serve these files.
RUN ln -s /var/www/app/static /var/www/ski_data-static
VOLUME /var/www/ski_data-static

# Expose the port where uWSGI will run
EXPOSE 5000

# If running this app behind a webserver using the uwsgi protocol (like nginx),
# then use --socket.  Otherwise run with --http to run as a full http server.
#CMD ["uwsgi", "--http", ":5000",         "--wsgi-file", "ski_data.py", "--callable", "app", "--processes",  "2", "--threads", "4"]
CMD ["uwsgi", "--socket", "0.0.0.0:5000", "--wsgi-file", "ski_data.py", "--callable", "app", "--processes",  "2", "--threads", "4"]