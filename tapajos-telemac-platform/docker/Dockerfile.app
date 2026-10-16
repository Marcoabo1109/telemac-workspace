FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libglu1-mesa libgl1 libgomp1 python3-gmsh libgmsh-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN cp /usr/lib/python3/dist-packages/gmsh.py /usr/local/lib/python3.11/site-packages/gmsh.py
COPY backend backend
COPY scripts scripts
COPY optimization optimization
COPY data data
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
