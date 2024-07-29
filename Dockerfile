# Use the base image with undetected-chromedriver and Chrome
FROM ultrafunk/undetected-chromedriver

# Set the working directory inside the container
WORKDIR /app

# Install additional dependencies
RUN apt-get update && \
    apt-get install -y \
    pulseaudio \
    pavucontrol \
    curl \
    sudo \
    libnss3-tools \
    ffmpeg \
    unzip \
    libfontconfig \
    libfreetype6 \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    xterm \
    vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add root to the audio group and pulse-access
RUN usermod -aG audio root && \
    adduser root pulse-access

# Environment variables for DBus and PulseAudio
ENV DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
ENV XDG_RUNTIME_DIR=/run/user/0

# Prepare DBus
RUN mkdir -p /run/dbus && \
    chmod 755 /run/dbus && \
    rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse && \
    dbus-daemon --system --fork

# Install PortAudio
RUN wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz && \
    tar -xvf pa_stable_v190700_20210406.tgz && \
    mv portaudio /usr/src/ && \
    cd /usr/src/portaudio && \
    ./configure && \
    make && \
    make install && \
    ldconfig

# Allow root to execute sudo without a password
RUN echo 'user ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    adduser root pulse-access && \
    mkdir -p /var/run/dbus && \
    dbus-uuidgen > /var/lib/dbus/machine-id

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure pulseaudio.conf is copied into the image
COPY pulseaudio.conf /app/pulseaudio.conf
RUN mv pulseaudio.conf /etc/dbus-1/system.d/pulseaudio.conf

# Copy your application code to the container
COPY . /app

# Set any required environment variables 
ENV BOT_NAME="WhisperBot"
ENV MEETING_LINK="https://meet.google.com/haw-buhx-quj"
ENV USER_ID="DEFAULT_USER"
ENV MEETING_ID="DEFAULT_MEETING_ID"
ENV AWS_BUCKET_NAME="online-meeting-audio-recordings"
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV CODE_EXECUTION_TIME_LIMIT="1"

# Define the command to run the main.py script
CMD ["python3", "main.py"]
