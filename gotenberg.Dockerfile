# Custom Gotenberg image with Thai / Windows fonts bundled
# Gotenberg 8 runs LibreOffice headless internally; it needs the same fonts
# that the DOCX files use to produce accurate, pixel-perfect PDFs.
FROM gotenberg/gotenberg:8

USER root

# Install fontconfig so fc-cache is available, plus curl for the container healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends fontconfig curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the font files we prepared on the host
COPY fonts/ /usr/share/fonts/custom/
COPY docker/fonts/local.conf /etc/fonts/local.conf

# Rebuild font cache
RUN fc-cache -fv

# Switch back to the restricted user Gotenberg ships with
USER gotenberg
