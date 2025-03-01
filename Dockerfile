FROM ubuntu:latest
LABEL authors="hsn"
# Build Python 3.11.10 and 3.9.20 from source
USER root

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install gcc wget -y
RUN apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libbz2-dev liblzma-dev sqlite3 libsqlite3-dev tk-dev uuid-dev libgdbm-compat-dev -y

ARG CPY_VER=3.13.2
RUN wget https://www.python.org/ftp/python/$CPY_VER/Python-$CPY_VER.tar.xz
RUN tar -xf Python-$CPY_VER.tar.xz
RUN cd Python-$CPY_VER && ./configure --enable-optimizations --with-lto && make -j 16 && make install && cd ..
RUN rm -rf Python-$CPY_VER Python-$CPY_VER.tar.xz

ARG PYPY_VER=3.11-v7.3.19
RUN wget https://downloads.python.org/pypy/pypy$PYPY_VER-linux64.tar.bz2
RUN tar -jxf pypy$PYPY_VER-linux64.tar.bz2
RUN mv pypy$PYPY_VER-linux64 /opt/pypy3
RUN ln -s /opt/pypy3/bin/pypy3 /usr/local/bin/pypy3

# Install Poetry
RUN pip3.13 install poetry # todo: use pythion ver head

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

RUN poetry install --no-root

COPY ./src /app/src
ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host","0.0.0.0","--port","8000"]
