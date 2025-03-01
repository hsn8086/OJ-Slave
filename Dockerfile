FROM ubuntu:latest
LABEL authors="hsn"
# Build Python 3.11.10 and 3.9.20 from source
USER root

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install gcc wget -y
RUN apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libbz2-dev liblzma-dev sqlite3 libsqlite3-dev tk-dev uuid-dev libgdbm-compat-dev -y

RUN wget https://www.python.org/ftp/python/3.11.10/Python-3.11.10.tar.xz
RUN tar -xf Python-3.11.10.tar.xz
RUN cd Python-3.11.10 && ./configure --enable-optimizations --with-lto && make -j 16 && make install && cd ..

RUN wget https://www.python.org/ftp/python/3.9.20/Python-3.9.20.tar.xz
RUN tar -xf Python-3.9.20.tar.xz
RUN cd Python-3.9.20 && ./configure --enable-optimizations --with-lto && make -j 16 && make install && cd ..

RUN rm -rf Python-3.11.10 Python-3.11.10.tar.xz Python-3.9.20 Python-3.9.20.tar.xz

# Install Poetry
RUN pip3.11 install poetry

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

RUN poetry install

COPY ./src /app/src
ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host","0.0.0.0","--port","8000"]
