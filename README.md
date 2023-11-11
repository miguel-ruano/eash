# Eash CLI
easy way to share your commands

## Requisitos

Se necesita tener instalado el setuptools para Python 3.

## Configuración

## Comandos

Los comandos del CLI son de carga dinámica. El núcleo provee algunos comandos esenciales para la configuración del CLI, pero le da la posibilidad al usuario de crear sus propios comandos a través de la creación de archivos YAML.

### Tipos de Comandos

En los comandos se pueden encontrar los siguientes tipos:
- `group` (para agrupación de comandos)
- `standard` (por defecto)

### Comando de Grupo

El comando de tipo `group` sirve en los casos que se necesite crear varios comandos con un concepto en común pero que estos no queden sueltos para el núcleo principal.

### Comando Estándar

El comando de tipo `standard` es el concepto predeterminado para ejecutar cualquier tarea a través de sus `steps`.

### Esquema

Los comandos se cargan a partir de una plantilla en formato YAML. El siguiente esquema detalla las opciones disponibles.

```yaml
# Esquema de comando
command: str (nombre del comando) (required)
help: str (required) (Descripción del comando)
# ... (resto del esquema)
```

### Expresiones de Análisis

Para la facilidad de configuración del comando, algunas propiedades pueden ser analizadas a ciertos valores contenidos en los contextos del comando.

```yaml
command: hello
help: un comando muy básico
arguments:
    - name: arg1
steps: 
    - type: command
      command: 'echo "Hola ${arg1}, ¿cómo estás?"'
```

Los contextos de referencia a valores son `core`, `command`, y `step`.

### Código Python

En ciertas condiciones, es necesario ejecutar código de alto nivel para ciertas tareas. Se habilita la posibilidad de ejecutar código Python, limitado a ciertas funciones proveídas por el núcleo.

```python
name == 'archivo_uno' and OS_VERSION == 'linux'  # Condición
zipdir(CWD_PATH + '/.~temp/package', CWD_PATH + '/' + filename)  # Ejecución de función
```

## Acciones Bundlers

Son acciones que se pueden ejecutar en los comandos ya sea de forma literal o a través de su carga de un archivo.

### Acciones Disponibles

A continuación se enumeran las acciones disponibles con su correspondiente sintaxis.

- `WORKDIR`: define el directorio actual de trabajo del bundler.
- `MKFILE`: realiza la creación de un archivo en el directorio actual de trabajo.
- `MKDIR`: realiza la creación de un directorio en el directorio actual de trabajo.
- `RMDIR`: realiza la eliminación de un directorio en el directorio actual de trabajo.
- `RUN`: realiza la ejecución de un comando del sistema operativo en el directorio de contexto dado.
- `CP`: realiza el copiado de uno o varios archivos (según el filtro dado) a un destino dado.

## Acción `WORKDIR`

Define el directorio actual de trabajo del bundler.

```bash
WORKDIR ${dir}
```

## Acción `MKFILE`

Realiza la creación de un archivo en el directorio actual de trabajo.

```bash
MKFILE file_name.txt
```

Contenido del archivo a crear:

```bash
    MKFILE file_name.txt  # ejecucion normal
    ```
    contenido del archivo a crear
    ```
    MKFILE ${file_name}_in_bundler.txt # ejecucion con variable
    ```
    un saludo a todo el equipo ${team_name}
    ```
```

## Acción `MKDIR`

Realiza la creación de un directorio en el directorio actual de trabajo.

```bash
MKDIR ${dir}
```

## Acción `RMDIR`

Realiza la eliminación de un directorio en el directorio actual de trabajo.

```bash
RMDIR ${dir}
```

## Acción `RUN`

Realiza la ejecución de un comando del sistema operativo en el directorio de contexto dado.

```bash
RUN ${dir} '${command}'
```

## Acción `CP`

Realiza el copiado de uno o varios archivos (según el filtro dado) a un destino dado.

```bash
CP '${filter}' '${dest}'
```

La acción `CP` tiene opciones adicionales:

- Para mantener la misma estructura del directorio origen:

  ```bash
  CP ./app/**/*.py package -r
  ```

- Para copiar un archivo único:

  ```bash
  CP ./lambda_handler.py dest/lambda_handler_copy.py
  ```

### Creación de Bundlers

Para la facilidad de la ejecución de los bundlers, se habilita la lectura de estos desde un archivo. El núcleo tiene bundlers definidos, pero también tiene la posibilidad de cargar bundlers personalizados.

Los bundlers personalizados son cargados a partir de un directorio configurado para este propósito.

```sh
# Para ver el directorio, ejecute
eash-cli settings get-bundler
```

En caso de no estar configurado, agregue un directorio con el siguiente comando.

```sh
eash-cli settings set-bundler 'my-dir'
```

Ejemplo:

```bash
MKDIR ${APP_NAME}
WORKDIR ${APP_NAME}
MKDIR app
MKFILE FILE_TEMPLATE.md
```

Puede hacer referencias escribiendo su path de acceso al archivo. No se debe agregar el directorio de donde son cargados los bundlers.

## Creación de Comandos Personalizados

Los comandos personalizados son cargados a partir de un directorio configurado para este propósito.

```sh
# Para ver el directorio, ejecute
eash-cli settings get-commands
```

En caso de no estar configurado, agregue un directorio con el siguiente comando.

```sh
eash-cli settings set-commands 'my-directorio'
```

Ejemplo:

```yaml
command: new
help: 'Crea un nuevo proyecto'
options:
  - name: dir
    type: str
    default: ${CWD_PATH}
    help: Directorio de creación del proyecto
steps:
  - message: Creando archivos base...
    type: bundler-action
    bundler:
      - init_workdir.anbr
      - standard_files.anbr
      - custom/my_bundler.anbr
    vars:
      - 'WORK_DIR:${dir}/app'
```
