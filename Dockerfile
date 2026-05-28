# ── Stage: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

# Enable contrib repositories for ttf-mscorefonts-installer and install dependencies
RUN sed -i 's/Components: main/Components: main contrib non-free/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    fontconfig \
    fonts-thai-tlwg \
    fonts-noto-cjk \
    ttf-mscorefonts-installer \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Install custom Thai/Windows fonts ───────────────────────────────────────
COPY fonts/ /usr/share/fonts/custom/
RUN fc-cache -fv

# ── App setup ───────────────────────────────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads temp_convert

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
