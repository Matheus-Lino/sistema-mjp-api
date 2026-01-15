from flask import Blueprint, jsonify, request
from connection import get_connection
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)

# =====================================================
# OFICINAS - GERENCIAMENTO
# =====================================================
@dashboard_bp.route("/oficinas", methods=["GET"])
def listar_oficinas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, cnpj, telefone, email, endereco, created_at FROM oficinas ORDER BY nome")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(dados)

@dashboard_bp.route("/oficinas", methods=["POST"])
def criar_oficina():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome")
        cnpj = data.get("cnpj", "")
        telefone = data.get("telefone", "")
        email = data.get("email", "")
        endereco = data.get("endereco", "")
        
        if not nome:
            return jsonify({"erro": "Nome da oficina é obrigatório"}), 400
        
        cursor.execute("""
            INSERT INTO oficinas (nome, cnpj, telefone, email, endereco, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nome, cnpj, telefone, email, endereco))
        
        nova_oficina_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "msg": "Oficina criada com sucesso",
            "oficina_id": nova_oficina_id
        }), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/oficinas/<int:oficina_id>", methods=["GET"])
def buscar_oficina(oficina_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM oficinas WHERE id = %s", (oficina_id,))
    oficina = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not oficina:
        return jsonify({"erro": "Oficina não encontrada"}), 404
    
    return jsonify(oficina)

# =====================================================
# LISTAR CLIENTES (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/clientes", methods=["GET"])
def listar_clientes():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            c.id,
            c.nome,
            c.telefone,
            c.email,
            c.cidade,
            c.status,
            COALESCE(COUNT(os.id), 0) AS total_servicos
        FROM clientes c
        LEFT JOIN ordens_servico os ON os.cliente_id = c.id
        WHERE c.oficina_id = %s
        GROUP BY c.id, c.nome, c.telefone, c.email, c.cidade, c.status
        ORDER BY c.nome
        """,
        (oficina_id,)
    )
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(dados)

# =====================================================
# CRIAR NOVO CLIENTE (COM OFICINA_ID)
# =====================================================
@dashboard_bp.route("/clientes", methods=["POST"])
def criar_cliente():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        nome = data.get("nome")
        telefone = data.get("telefone", "")
        email = data.get("email", "")
        cidade = data.get("cidade", "")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")

        if not nome:
            return jsonify({"erro": "Nome é obrigatório"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        cursor.execute("""
            INSERT INTO clientes (nome, telefone, email, cidade, status, oficina_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, telefone, email, cidade, status, oficina_id))

        novo_cliente_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "msg": "Cliente criado com sucesso",
            "cliente_id": novo_cliente_id
        }), 201

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# EDITAR CLIENTE (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/clientes/<int:cliente_id>", methods=["PUT"])
def editar_cliente(cliente_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        nome = data.get("nome")
        telefone = data.get("telefone", "")
        email = data.get("email", "")
        cidade = data.get("cidade", "")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")

        if not nome:
            return jsonify({"erro": "Nome é obrigatório"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        cursor.execute("""
            UPDATE clientes 
            SET nome = %s, telefone = %s, email = %s, cidade = %s, status = %s
            WHERE id = %s AND oficina_id = %s
        """, (nome, telefone, email, cidade, status, cliente_id, oficina_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Cliente atualizado com sucesso"}), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# DELETAR CLIENTE (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/clientes/<int:cliente_id>", methods=["DELETE"])
def deletar_cliente(cliente_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar se o cliente tem ordens de serviço vinculadas
        cursor.execute("""
            SELECT COUNT(*) as count FROM ordens_servico 
            WHERE cliente_id = %s AND oficina_id = %s
        """, (cliente_id, oficina_id))
        resultado = cursor.fetchone()
        
        if resultado["count"] > 0:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Não é possível deletar cliente que possui ordens de serviço"}), 400

        # Verificar se o cliente tem veículos vinculados
        cursor.execute("""
            SELECT COUNT(*) as count FROM veiculos 
            WHERE cliente_id = %s AND oficina_id = %s
        """, (cliente_id, oficina_id))
        veiculos_result = cursor.fetchone()

        if veiculos_result["count"] > 0:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Não é possível deletar cliente que possui veículos vinculados"}), 400

        cursor.execute("""
            DELETE FROM clientes 
            WHERE id = %s AND oficina_id = %s
        """, (cliente_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Cliente deletado com sucesso"}), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# LISTAR VEÍCULOS (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/veiculos", methods=["GET"])
def listar_veiculos():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            v.id,
            v.placa,
            v.modelo,
            v.marca,
            v.ano,
            v.km,
            v.cliente_id,
            c.nome AS proprietario_nome,
            v.created_at
        FROM veiculos v
        LEFT JOIN clientes c ON c.id = v.cliente_id
        WHERE v.oficina_id = %s
        ORDER BY v.marca, v.modelo
    """, (oficina_id,))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(dados)

# =====================================================
# CRIAR NOVO VEÍCULO (COM OFICINA_ID)
# =====================================================
@dashboard_bp.route("/veiculos", methods=["POST"])
def criar_veiculo():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        placa = data.get("placa", "")
        modelo = data.get("modelo", "")
        marca = data.get("marca", "")
        ano = data.get("ano")
        km = data.get("km")
        cliente_id = data.get("cliente_id")
        oficina_id = data.get("oficina_id")

        if not placa or not modelo or not marca:
            return jsonify({"erro": "Placa, modelo e marca são obrigatórios"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        cursor.execute("""
            INSERT INTO veiculos (placa, modelo, marca, ano, km, cliente_id, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (placa, modelo, marca, ano, km, cliente_id, oficina_id))

        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Veículo criado com sucesso", "veiculo_id": novo_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# EDITAR VEÍCULO (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/veiculos/<int:veiculo_id>", methods=["PUT"])
def editar_veiculo(veiculo_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        placa = data.get("placa", "")
        modelo = data.get("modelo", "")
        marca = data.get("marca", "")
        ano = data.get("ano")
        km = data.get("km")
        cliente_id = data.get("cliente_id")
        oficina_id = data.get("oficina_id")
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        cursor.execute("""
            UPDATE veiculos
            SET placa = %s, modelo = %s, marca = %s, ano = %s, km = %s, cliente_id = %s
            WHERE id = %s AND oficina_id = %s
        """, (placa, modelo, marca, ano, km, cliente_id, veiculo_id, oficina_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Veículo atualizado com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# DELETAR VEÍCULO (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/veiculos/<int:veiculo_id>", methods=["DELETE"])
def deletar_veiculo(veiculo_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar vínculo com ordens de serviço
        cursor.execute("""
            SELECT COUNT(*) AS total FROM ordens_servico 
            WHERE veiculo_id = %s AND oficina_id = %s
        """, (veiculo_id, oficina_id))
        resultado = cursor.fetchone()
        if resultado and resultado.get("total", 0) > 0:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Não é possível excluir veículo vinculado a ordens de serviço"}), 400

        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM veiculos 
            WHERE id = %s AND oficina_id = %s
        """, (veiculo_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Veículo excluído com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# LISTAR SERVIÇOS (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/servicos", methods=["GET"])
def listar_servicos():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id, 
            nome, 
            COALESCE(preco_base, 0) as preco, 
            COALESCE(tempo_estimado, 0) as duracao
        FROM servicos 
        WHERE oficina_id = %s
        ORDER BY nome
    """, (oficina_id,))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(dados)

# Continue com os outros endpoints...
