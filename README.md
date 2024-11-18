# Gateway

Para ejecutar el gateway desde local usando un ambiente de Docker solo se necesita seguir los siguientes pasos:

## Crear la network donde van a correr los contenedores en local con docker
        docker network create abc-call-network

## En el proyecto de gateway entrar a la carpeta local
        cd local

## Ejecutar el comando
        docker compose up -d
