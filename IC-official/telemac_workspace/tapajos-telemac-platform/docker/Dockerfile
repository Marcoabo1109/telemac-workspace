# Same source build for linux/amd64 and linux/arm64; no x86-only compiler flags.
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates gfortran gcc g++ make cmake libopenmpi-dev openmpi-bin libmetis-dev python3 python3-pip python3-dev libglu1-mesa libgl1 ffmpeg python3-gmsh libgmsh-dev && rm -rf /var/lib/apt/lists/*
# Python 3.11 built from official source; Ubuntu 22.04 system Python remains 3.10.
RUN apt-get update && apt-get install -y --no-install-recommends curl libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev && curl -fSL https://www.python.org/ftp/python/3.11.14/Python-3.11.14.tgz -o /tmp/python.tgz && tar -xzf /tmp/python.tgz -C /tmp && cd /tmp/Python-3.11.14 && ./configure --prefix=/usr/local && make -j2 && make altinstall && rm -rf /tmp/Python* /tmp/python.tgz /var/lib/apt/lists/*
RUN python3.11 -m pip install 'numpy<2' scipy matplotlib mpi4py
ARG TELEMAC_REF=v8p5r0
RUN git clone --depth 1 --branch ${TELEMAC_REF} https://gitlab.pam-retd.fr/otm/telemac-mascaret.git /opt/telemac
ENV HOMETEL=/opt/telemac SYSTELCFG=/opt/telemac/configs/systel-platform.cfg USETELCFG=gnu
ENV PATH=/opt/telemac/scripts/python3:/usr/local/bin:$PATH
ENV PYTHONPATH=/opt/telemac/scripts/python3
COPY docker/systel.cfg /opt/telemac/configs/systel-platform.cfg
RUN python3.11 /opt/telemac/scripts/python3/compile_telemac.py -j 2
WORKDIR /app
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt
RUN cp /usr/lib/python3/dist-packages/gmsh.py /usr/local/lib/python3.11/site-packages/gmsh.py
COPY backend backend
COPY scripts scripts
COPY optimization optimization
COPY data data
ENV TELEMAC_EXECUTABLE=/app/docker/run-telemac
COPY docker/run-telemac /app/docker/run-telemac
RUN chmod +x /app/docker/run-telemac
EXPOSE 8000 8888 11111
CMD ["python3.11","-m","uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
