from utilities.imports import *
from werkzeug.utils import secure_filename
from flask import redirect, url_for
app_catalogo = Blueprint('app_catalogo', __name__, url_prefix='/catalogo')

config = GlobalConfig()



@app_catalogo.route('/Roles/Alta', methods=['POST', 'GET'])
def roles_alta():
    with VerificarPermisosUsuario("RolesAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    if request.method == 'POST':
        with VerificarPermisosUsuario("RolesAlta", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        rol_name = request.form.get('rol_name')
        informacion = request.form.get('informacion')

        if rol_name:
            new_rol = cv.Roles.add(rol_name,informacion,[])
            if new_rol:
                # Retorna un mensaje JSON si la inserción fue exitosa
                return jsonify({'estatus': True, 'status': 'success'}), 201
            else:
                # Retorna un mensaje JSON si la inserción falló
                return jsonify({'estatus': False, 'status': 'error'}), 500
        return jsonify({'estatus': False, 'status': 'error'}), 500
    else:
        # Renderiza el formulario HTML para crear un usuario
        return render_template('scaizen/roles_crear.html')

@app_catalogo.route('/Roles/Consultar', methods=['POST', 'GET'])
def roles_consultar():
    with VerificarPermisosUsuario("RolesConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    elementos_por_pagina = 10
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        with VerificarPermisosUsuario("RolesConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        id_usuarios = request.form.get('id_usuarios')
        id = request.form.get('id')

        eliminar = request.form.get('eliminar')

        if id_usuarios and not eliminar:
            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina

            # Obtener datos de clientes existentes
            roles_existentes,total = cv.Roles.select_for_pagination(page_num,elementos_por_pagina)

            total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total)
            if end_index > total:
                end_index = total

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
            if roles_existentes:
                data = cv.query_to_json(roles_existentes)
                logging.debug(data)
                user_perms = []
                if config.CHECK_USER_PERM("RolesEditar",current_user.RolPerms): user_perms.append("RolesEditar")
                if config.CHECK_USER_PERM("RolesEditarPermisos",current_user.RolPerms): user_perms.append("RolesEditarPermisos")
                if config.CHECK_USER_PERM("RolesEliminar",current_user.RolPerms): user_perms.append("RolesEliminar")

                return jsonify({'datos_roles_consulta': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 
                                'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num,'user_perms': user_perms})
            else:
                return jsonify({'estatus': False, 'status': 'No clients found'}), 404

        elif id and eliminar == "eliminar":
            with VerificarPermisosUsuario("RolesEliminar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            try:
                id_desencriptada = config.desencriptar_desde_hex(clave_hex_hash,id)
                rol = cv.Roles.select_by_IdRol(id_desencriptada)
                if current_user.RolName == rol.NombreRol:
                    return jsonify({'estatus': False, 'status': 'error', 'error':'No puedes borrar el rol que utilizas.'})
                delete_rol = cv.Roles.delete(id_desencriptada)
                
                if not delete_rol:
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error', 'error':delete_rol}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500   
    return render_template('scaizen/roles_consultar.html')

@app_catalogo.route('/Roles/Editar', methods=['POST', 'GET'])
@login_required
def roles_editar():
    with VerificarPermisosUsuario("RolesEditar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("RolesEditar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        id_t = request.form.get('actualizar')
        if id_t:
            id_rol = config.desencriptar_desde_hex(clave_hex_hash, id_t)
            rol_especifico = cv.Roles.select_by_IdRol(id_rol)
            logging.debug(rol_especifico)
            if rol_especifico:
                rol_especifico.IdRol = config.encriptar_a_hex(clave_hex_hash,rol_especifico.IdRol)
                rol_especifico = cv.query_to_json([rol_especifico])[0]
                return jsonify({'datos_rol_especifico': rol_especifico})
            else:
                return jsonify({'estatus': False, 'status': 'no_data'}), 404

        rol_name = request.form.get('rol_name')
        informacion = request.form.get('informacion')
        editar = request.form.get('editar')
        actualizar_id = request.form.get('actualizar_id') 
        
        if editar and  actualizar_id and rol_name:
            id_rol = config.desencriptar_desde_hex(clave_hex_hash, actualizar_id)
            rol = cv.Roles.select_by_IdRol(id_rol)
            edit_edit = cv.Roles.update(id_rol,nombreRol=rol_name, descripcion=informacion)
            if edit_edit != rol:
                return jsonify({'estatus': True, 'status': 'success'}), 200
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500
            
    return render_template('scaizen/roles_editar.html')

@app_catalogo.route('/Roles/EditarPermisos/<string:id>', methods=['POST', 'GET'])
@login_required
def permisos_editar(id):
    with VerificarPermisosUsuario("RolesEditarPermisos", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("RolesEditarPermisos", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        operacion = request.form.get('operacion')
        if operacion:
            if operacion == "edit_perm":
                
                permisos = request.form.getlist('perms[]')
                id_rol = config.desencriptar_desde_hex(clave_hex_hash, id)
                rol = cv.Roles.select_by_IdRol(id_rol)
                if len(permisos) > 0:
                    logging.debug('hay permisos')
                    perms = config.FORMATEAR_PERMISOS(permisos)
                    logging.debug(perms)
                    rol_especifico = cv.Roles.update(id_rol, permisos=perms)
                else: 
                    logging.debug('permisos vacios')
                    rol_especifico = cv.Roles.update(id_rol, permisos=[])

                if rol != rol_especifico:
                    return jsonify({'estatus': True,
                                        'msg': 'Los permisos de lo han sido actualizado.'})
                else:
                    return jsonify({'estatus': False, 'error': 'No se puedo actualizar los permisos'}), 404
        
    id_rol = config.desencriptar_desde_hex(clave_hex_hash, id)
    rol_especifico = cv.Roles.select_by_IdRol(id_rol)
    
    if not rol_especifico: return redirect(url_for('app_catalogo.roles_consultar'))
    
    return render_template('scaizen/permisos_editar.html', rol=rol_especifico, permisos=config.PERMISOS_VALIDOS)
