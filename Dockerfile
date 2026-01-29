# Usa una imagen base de Python (elige la versión adecuada para tu aplicación)
FROM python:3.10.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias (por ejemplo, Flask y cualquier otro paquete necesario)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --timeout=200

# Configura las variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Define el comando para ejecutar tu aplicación Flask
CMD ["python", "app.py", "-b", "0.0.0.0:5000"]
