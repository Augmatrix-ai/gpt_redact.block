FROM ubuntu:focal-20230605

# Set the timezone without interaction
ENV DEBIAN_FRONTEND=noninteractive
# Update the package repository and install necessary packages
RUN apt-get update && \
    apt-get install -y \
    zip \
    python3-dev \
    python3-pip \
    libmysqlclient-dev \
    build-essential \
    python3-virtualenv \
    poppler-utils \
    ghostscript \
    curl \
	git \
    screen && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata && \
    apt-get install -y libglib2.0-0 libgl1 
# Set the timezone without interaction
ENV TZ=UTC
# Set the timezone without interaction

# Copy files
RUN mkdir /app
COPY ./ /app/.
COPY /deployment/entrypoint.sh .

# Install Python packages
RUN pip3 install -r /app/requirments.txt

# Set permissions and convert line endings
RUN chmod +x entrypoint.sh && \
    sed -i -e 's/\r$//' entrypoint.sh

# Set the entry point
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["sleep", "infinity"]

