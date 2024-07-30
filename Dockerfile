
# Use the base image with undetected-chromedriver and Chrome

FROM datawookie/undetected-chromedriver:latest

# Set the working directory inside the container
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    pulseaudio \
    pavucontrol \
    curl \
    sudo \
    xvfb \
    libnss3-tools \
    ffmpeg \
    xdotool \
    unzip \
    x11vnc \
    libfontconfig \
    libfreetype6 \
    xfonts-scalable \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    xterm \
    vim \
    dbus

RUN usermod -aG audio root
RUN adduser root pulse-access
ENV key=value DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
ENV XDG_RUNTIME_DIR=/run/user/0
RUN mkdir -p /run/dbus
RUN chmod 755 /run/dbus
RUN rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse
RUN dbus-daemon --system --fork
RUN wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
RUN tar -xvf pa_stable_v190700_20210406.tgz
RUN mv portaudio /usr/src/


WORKDIR /usr/src/portaudio
RUN ./configure && \
    make && \
    make install && \
    ldconfig
RUN echo 'user ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN adduser root pulse-access
RUN mkdir -p /var/run/dbus
RUN dbus-uuidgen > /var/lib/dbus/machine-id
#RUN dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

WORKDIR /app

RUN touch /root/.Xauthority
RUN chmod 600 /root/.Xauthority
RUN rm /run/dbus/pid
COPY pulseaudio.conf .
RUN mv pulseaudio.conf /etc/dbus-1/system.d/pulseaudio.conf

# Download and install Chrome and Chromedriver
ENV CHROME_VERSION=127.0.6533.72
ENV CHROMEDRIVER_VERSION=126.0.6478.126
RUN wget https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    wget https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip -o -qq chrome-linux64.zip -d /var/local/ && \

# Set up X authority
RUN touch /root/.Xauthority && \
    chmod 600 /root/.Xauthority && \
    rm /run/dbus/pid
    
# Ensure pulseaudio.conf is copied into the image
COPY pulseaudio.conf /app/pulseaudio.conf
RUN mv /app/pulseaudio.conf /etc/dbus-1/system.d/pulseaudio.conf


# Update chrome to version 127
# Define the version variables
ENV CHROME_VERSION=127.0.6533.72
ENV CHROMEDRIVER_VERSION=126.0.6478.126

# Download Chrome and Chromedriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    wget https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip

# Install Chrome and Chromedriver
RUN unzip -o -qq chrome-linux64.zip -d /var/local/ && \

    
# Print Chrome and Chromedriver versions
RUN /bin/sh -c "echo 'Chrome: $(chrome --version)' && echo 'ChromeDriver: $(chromedriver --version)'"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .


# Print Chrome Version 
RUN /bin/sh -c echo "Chrome: $(chrome --version | sed 's/.* \([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\) *$/\1/')" && \ 
    echo "ChromeDriver: $(chromedriver --version | sed 's/.* \([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\) .*$/\1/')"

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .
# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .



# Set other required environment variables

ENV BOT_NAME="WhisperBot"
ENV MEETING_LINK="https://meet.google.com/haw-buhx-quj"
ENV USER_ID="DEFAULT_USER"
ENV MEETING_ID="DEFAULT_MEETING_ID"
ENV AWS_BUCKET_NAME="online-meeting-audio-recordings"
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV CODE_EXECUTION_TIME_LIMIT="1"

# Define the command to run the application
CMD ["python3", "main.py"]
