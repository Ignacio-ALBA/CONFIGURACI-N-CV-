from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# Datos de ejemplo (una lista de elementos)
elementos = list(range(1, 101))

# Configuración para la paginación
elementos_por_pagina = 10

@app.route('/')
def index():
    # Obtener el número de página de los argumentos de la solicitud
    page_num = request.args.get('page', 1, type=int)
    print(page_num)
    # Calcular el índice de inicio y final para la lista paginada
    start_index = (page_num - 1) * elementos_por_pagina
    end_index = start_index + elementos_por_pagina

    # Obtener la lista de elementos para la página actual
    elementos_paginados = elementos[start_index:end_index]

    # Calcular el número total de páginas
    total_pages = len(elementos) // elementos_por_pagina + (len(elementos) % elementos_por_pagina > 0)

    # Crear el objeto de paginación
    pagination = {
        'links': {
            'prev': url_for('index', page=page_num - 1) if page_num > 1 else None,
            'next': url_for('index', page=page_num + 1) if page_num < total_pages else None
        }
    }

    return render_template('index.html', elementos=elementos_paginados, pagination=pagination, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
