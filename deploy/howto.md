# How to deploy

Here are some suggestions on how to deploy the app.

## Prepare

1. Make sure you have python3 installed and things like sqlite3, NGINX and uwsgi.
2. Create a (system) user without home folder specific for this website.
3. Create a directory to run the application from (eg. ``/srv/www/home_dashboard``)
4. create a python3 virtual environment in this directory
5. Install NGINX
6. Create (or obtain) as SSL certificate and install it with NGINX.

### uWSGI

1. copy all the code from the repository to you application directory.
2. write the uwsgi script (see the ``home_dashboard_uwsgi.ini`` script as an example)
3. test the script: ``sudo uwsgi home_dashboard.uwsgi``
4. create a startup script to create the uwsgi socket (see home_dashboard_startup) and install it in ``/etc/init.d``
5. Start the script and have it start on startup ``sudo update-rc.d home_dashboard_startup defaults``

### NGINX

1. make a site for NGINX (see nginx_setup.conf)

## Deploy

1. Backup your environment files like ``settings.py`` and any database files.
2. Copy the new deploy: ``rsync -avr SOURCE DEST --delete-after
3. Move the environment files back to their location
4. Check file permissions
5. Run a ``./manage.py migrate``
6. Run a ``./manage.py check --deploy`` and fix any issues
7. Restart your uWSGI and NGINX services
8. Create your admin user (and other users)
