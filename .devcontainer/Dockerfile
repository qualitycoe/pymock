# Use the official Python 3.12 dev container base image
FROM mcr.microsoft.com/devcontainers/python:1-3.12

# Install OS packages required for downloading and installing the font
RUN apt-get update && apt-get install -y wget unzip fontconfig

# Download and install JetBrainsMono Nerd Font Propo
RUN wget -O /tmp/JetBrainsMono.zip https://github.com/ryanoasis/nerd-fonts/releases/download/v2.3.3/JetBrainsMono.zip \
    && mkdir -p /usr/local/share/fonts/JetBrainsMono \
    && unzip /tmp/JetBrainsMono.zip -d /usr/local/share/fonts/JetBrainsMono \
    && fc-cache -fv \
    && rm /tmp/JetBrainsMono.zip

# Upgrade pip and install Hatch and its build tools globally
RUN pip install --upgrade pip && pip install hatch hatchling hatch-vcs
