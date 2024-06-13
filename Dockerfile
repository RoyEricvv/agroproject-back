FROM mlupin/docker-lambda:python3.9-build
ENV PYTHONUNBUFFERED 1
WORKDIR /var/task

RUN pip install -U pip-tools && \
    pip install -U zappa

RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\] "' >> /root/.bashrc

CMD ["bash"]

# COPY requirements.txt requirements.txt

# # Instalar las dependencias
# RUN pip install --no-cache-dir -r requirements.txt

# # Copiar el resto del código de la aplicación
# COPY . .

# # Establecer la variable de entorno para Flask
# ENV FLASK_APP=app.py

# # Instalar Mangum, que es necesario para usar ASGI en Lambda
# RUN pip install mangum

# # Configurar el prompt del shell
# RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\] "' >> /root/.bashrc

# # Comando para ejecutar Lambda
# CMD ["app.lambda_handler"]