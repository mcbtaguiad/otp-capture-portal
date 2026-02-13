FROM alpine:3
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# define variables

# make sure these variables are set the same as `docker-entrypoint.sh`
ENV CONFIG_MOUNT="/config"
ENV OTPSPOT_DIR="/otpspot"
ENV WEB_PORT=8000
ENV BUSINESS_NAME="Good Coffee"
ENV ADMIN_USERNAME="admin"
ENV ADMIN_PASSWORD="password123"

RUN apk add --upgrade --no-cache sudo \
    pamtester \
    google-authenticator \
    py3-flask \
    libqrencode \
    py3-gunicorn \
    py3-otp \
    py3-qrcode \
    py3-pillow

# install otpspot
ADD /app/config $CONFIG_MOUNT
ADD /app/web $OTPSPOT_DIR/web
ADD /app/index.html $OTPSPOT_DIR
ADD /app/otpspot.py $OTPSPOT_DIR
ADD /app/wsgi.py $OTPSPOT_DIR
ADD /app/template_pam /etc/pam.d/otpspot

# Expose network services
EXPOSE $WEB_PORT

# Install entrypoint
COPY docker-entrypoint.sh /
ENTRYPOINT ["/bin/sh","/docker-entrypoint.sh"]

# Start otpspot
CMD ["otpspot"]
