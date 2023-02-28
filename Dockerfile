FROM python:3.10-slim as python_base310

# install dependendies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl dnsutils net-tools && \
    apt-get install --reinstall -y locales && \
    sed -i 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8;


WORKDIR /opt/cigar_project

COPY requirements.txt ./

# no cache
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py entrypoint.sh alembic.ini logging_config.ini ./

# use unprivileged users
RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

ENTRYPOINT sh entrypoint.sh