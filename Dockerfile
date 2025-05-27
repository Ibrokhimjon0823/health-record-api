# pull official base image
FROM python:3.12-slim-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME


# install system dependencies
RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt-get -y install \
    --no-install-recommends \
    wget \
    curl \
    netcat \
    postgresql-client \
    build-essential \
    libpq-dev


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /home/app/web/entrypoint.sh
RUN chmod +x /home/app/web/entrypoint.sh

# Copy project
COPY . $APP_HOME
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]