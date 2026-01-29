# Usar una imagen base de Ubuntu
FROM ubuntu:22.04

# Variables de entorno
ARG XAMPP_URL

# Establece la zona horaria
ENV TZ=America/Mexico_City

RUN apt-get update && \
    apt-get install -y tzdata wget unzip && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Descargar e instalar XAMPP
RUN wget -O /tmp/xampp-installer.run $XAMPP_URL && \
    chmod +x /tmp/xampp-installer.run && \
    /tmp/xampp-installer.run --mode unattended && \
    rm /tmp/xampp-installer.run

# Modificar el archivo de configuración de Apache para phpMyAdmin
RUN sed -i 's/Require local/Require all granted/' /opt/lampp/etc/extra/httpd-xampp.conf

# Exponer puertos
EXPOSE 80 3306

# Comando para iniciar XAMPP
CMD ["/bin/bash", "-c", "/opt/lampp/lampp start && tail -f /dev/null"]
