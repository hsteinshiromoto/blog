# ---
# Build arguments
# ---
ARG DOCKER_PARENT_IMAGE
FROM $DOCKER_PARENT_IMAGE

# NB: Arguments should come after FROM otherwise they're deleted
ARG BUILD_DATE

# Silence debconf
ARG DEBIAN_FRONTEND=noninteractive

ARG PROJECT_NAME
ARG PYTHON_VERSION=3.11
# ---
# Enviroment variables
# ---
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
ENV TZ Australia/Sydney
ENV JUPYTER_ENABLE_LAB=yes
ENV SHELL /bin/bash
ENV PROJECT_NAME=$PROJECT_NAME
ENV HOME /home/$PROJECT_NAME
ENV PYTHON_VERSION=$PYTHON_VERSION

# Set container time zone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL org.label-schema.build-date=$BUILD_DATE \
        maintainer="Humberto STEIN SHIROMOTO <h.stein.shiromoto@gmail.com>"

# ---
# Install pyenv
#
# References:
#   [1] https://stackoverflow.com/questions/65768775/how-do-i-integrate-pyenv-poetry-and-docker
# ---

RUN git clone --depth=1 https://github.com/pyenv/pyenv.git $HOME/.pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

# ---
# Install Python and set the correct version
# ---
RUN pyenv install $PYTHON_VERSION && pyenv global $PYTHON_VERSION

# ---
# Copy Container Setup Scripts
# ---
COPY bin/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY pyproject.toml /usr/local/pyproject.toml
# COPY poetry.lock /usr/local/poetry.lock

RUN chmod +x /usr/local/bin/entrypoint.sh

# Create the "home" folder
RUN mkdir -p $HOME
WORKDIR $HOME

# Get poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:$HOME/.poetry/bin"
ENV PATH="${PATH}:$HOME/.local/bin"

RUN poetry config virtualenvs.create false \
    && cd /usr/local/ \
    && poetry install --no-interaction --no-ansi

RUN poetry update --no-interaction --no-ansi

ENV PATH="${PATH}:$HOME/.local/bin"
# Need for Pytest
ENV PATH="${PATH}:${PYENV_ROOT}/versions/$PYTHON_VERSION/bin"

EXPOSE 8888
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]