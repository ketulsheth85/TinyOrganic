ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}-slim as core
ARG APP_DIR=/app
ARG BACKEND_APP_PORT=8000

ENV APP_DIR=${APP_DIR} \
    PIP_NO_CACHE_DIR=1 \
    PIP_COMPILE=0 \
    PYTHONDOONTWRITEBYTECODE=1 \
    PYTHONPATH=$PYTHONPATH:$APP_DIR \
    PYTHONUNBUFFERED=1

RUN mkdir -p /install

FROM core AS builder
WORKDIR /install 

COPY requirements/* /install/

RUN apt-get update && \
    apt-get install -y \
            build-essential \
            gcc \
            postgresql \
            procps \
            curl libjpeg-dev zlib1g && \
    pip install -r /install/00-install-pip.txt \
                       -r /install/01-needs-to-compile.txt \
                       -r /install/02-core.txt && \
    pip install Django==3.2 gunicorn==20.0.4 supervisor==4.2.2 newrelic==7.6.0.173 \
    whitenoise==5.3

FROM builder as backend-production
ARG DJANGO_STATIC_ROOT=/static
WORKDIR $APP_DIR
ENV PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production

COPY --from=builder /install /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /install /app/.local

COPY . .

COPY docker-entrypoint.sh /usr/local/bin
COPY health-check.sh health-check.sh
COPY ./config/launch-gunicorn-prod.sh ./config/
COPY ./config/newrelic.ini ./config/
COPY ./config/gunicorn.py ./config/
COPY ./config/supervisord.conf /etc/

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "health-check.sh" ]

ENTRYPOINT [ "docker-entrypoint.sh" ]

EXPOSE $BACKEND_APP_PORT

FROM backend-production as celery-production
ARG DJANGO_STATIC_ROOT=/static
ENV PYTHONDONTWRITEBYTECODE=1
#
#
#WORKDIR $APP_DIR
#COPY --from=builder /install /usr/local/lib/python${PYTHON_VERSION}/site-packages
#COPY --from=builder /install /app/.local

COPY celery/docker-entrypoint.sh /usr/local/bin
COPY celery/health-check.sh /usr/local/bin

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "health-check.sh" ]
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["worker"]


FROM celery-production as celerybeat-production
CMD ["beat"]
