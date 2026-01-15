from flask import Blueprint, jsonify, request
from connection import get_connection
from datetime import datetime
import bcrypt

dashboard_bp = Blueprint("dashboard", __name__)

# =====================================================
# FUNÇÕES DE SEGURANÇA
# =====================================================
def hash_password(password):
    """Gera hash de senha usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

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

@dashboard_bp.route("/oficinas/<int:oficina_id>", methods=["PUT"])
def atualizar_oficina(oficina_id):
    data = request.get_json()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE oficinas 
            SET nome = %s, cnpj = %s, telefone = %s, email = %s, endereco = %s
            WHERE id = %s
        """, (
            data.get("nome"),
            data.get("cnpj"),
            data.get("telefone"),
            data.get("email"),
            data.get("endereco"),
            oficina_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"mensagem": "Oficina atualizada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 500

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

    # Inclui total de serviços (ordens de serviço) por cliente
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
        LEFT JOIN ordens_servico os ON os.cliente_id = c.id AND os.oficina_id = %s
        WHERE c.oficina_id = %s
        GROUP BY c.id, c.nome, c.telefone, c.email, c.cidade, c.status
        ORDER BY c.nome
        """,
        (oficina_id, oficina_id)
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
        LEFT JOIN clientes c ON c.id = v.cliente_id AND c.oficina_id = %s
        WHERE v.oficina_id = %s
        ORDER BY v.marca, v.modelo
    """, (oficina_id, oficina_id))
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

# =====================================================
# LISTAR ORDENS DE SERVIÇO (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/ordens-servico", methods=["GET"])
def listar_ordens_servico():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.id AS ordem_id,
            c.nome AS nome_cliente,
            v.marca AS marca_veiculo,
            v.modelo AS modelo_veiculo,
            GROUP_CONCAT(DISTINCT s.nome SEPARATOR ', ') AS servico_nome,
            o.status,
            o.total,
            o.observacao,
            COUNT(DISTINCT f.id) AS tem_financeiro
        FROM ordens_servico o
        INNER JOIN clientes c ON c.id = o.cliente_id AND c.oficina_id = %s
        INNER JOIN veiculos v ON v.id = o.veiculo_id AND v.oficina_id = %s
        LEFT JOIN ordem_servico_servicos oss ON oss.ordem_servico_id = o.id
        LEFT JOIN servicos s ON s.id = oss.servico_id AND s.oficina_id = %s
        LEFT JOIN financeiro f ON f.ordem_servico_id = o.id AND f.oficina_id = %s
        WHERE o.oficina_id = %s
        GROUP BY o.id, c.nome, v.marca, v.modelo, o.status, o.total, o.observacao, o.created_at
        ORDER BY o.created_at DESC
    """, (oficina_id, oficina_id, oficina_id, oficina_id, oficina_id))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(dados)

# =====================================================
# CRIAR NOVA ORDEM DE SERVIÇO (COM OFICINA_ID)
# =====================================================
@dashboard_bp.route("/ordens-servico", methods=["POST"])
def criar_ordem_servico():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cliente_id = data.get("cliente_id")
        veiculo_id = data.get("veiculo_id")
        servico_ids = data.get("servico_ids", [])
        oficina_id = data.get("oficina_id")

        # Validação
        if not cliente_id or cliente_id == "":
            return jsonify({"erro": "Cliente é obrigatório"}), 400
        
        if not veiculo_id or veiculo_id == "":
            return jsonify({"erro": "Veículo é obrigatório"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        # Converter para int se necessário
        cliente_id = int(cliente_id)
        veiculo_id = int(veiculo_id)

        cursor.execute("""
            INSERT INTO ordens_servico (cliente_id, veiculo_id, status, total, observacao, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            cliente_id,
            veiculo_id,
            data.get("status", "Aberta"),
            data.get("total", 0),
            data.get("observacao", ""),
            oficina_id
        ))

        nova_ordem_id = cursor.lastrowid

        # Inserir serviços na tabela de relacionamento
        if servico_ids:
            for servico_id in servico_ids:
                cursor.execute("""
                    INSERT INTO ordem_servico_servicos (ordem_servico_id, servico_id)
                    VALUES (%s, %s)
                """, (nova_ordem_id, int(servico_id)))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "msg": "Ordem criada com sucesso",
            "ordem_id": nova_ordem_id
        }), 201

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# EDITAR ORDEM DE SERVIÇO (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/ordens-servico/<int:id>", methods=["PUT"])
def editar_ordem_servico(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        oficina_id = data.get("oficina_id")
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400

        # Busca OS atual
        cursor.execute("""
            SELECT status, total FROM ordens_servico 
            WHERE id = %s AND oficina_id = %s
        """, (id, oficina_id))
        os_atual = cursor.fetchone()

        if not os_atual:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Ordem de serviço não encontrada"}), 404

        status_antigo = os_atual["status"]
        novo_status = data["status"]
        novo_total = float(data["total"])
        
        # Validação: total não pode ser maior que 99999999.99 (limite DECIMAL(10,2))
        if novo_total > 99999999.99:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Valor total muito grande. Máximo permitido: R$ 99.999.999,99"}), 400
        
        if novo_total < 0:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Valor total não pode ser negativo"}), 400

        # Atualiza OS
        cursor.execute("""
            UPDATE ordens_servico
            SET status = %s,
                total = %s,
                observacao = %s
            WHERE id = %s AND oficina_id = %s
        """, (
            novo_status,
            novo_total,
            data.get("observacao"),
            id,
            oficina_id
        ))

        # ===============================
        # CONTROLE FINANCEIRO CORRETO
        # ===============================
        if novo_status.lower() == "finalizada":
            cursor.execute("""
                SELECT id FROM financeiro
                WHERE ordem_servico_id = %s AND tipo = 'Receita' AND oficina_id = %s
            """, (id, oficina_id))
            receita = cursor.fetchone()

            if receita:
                # 🔁 Atualiza valor da receita
                cursor.execute("""
                    UPDATE financeiro
                    SET valor = %s
                    WHERE ordem_servico_id = %s AND tipo = 'Receita' AND oficina_id = %s
                """, (novo_total, id, oficina_id))
            else:
                # ➕ Cria receita
                cursor.execute("""
                    INSERT INTO financeiro
                    (ordem_servico_id, tipo, valor, oficina_id, created_at)
                    VALUES (%s, 'Receita', %s, %s, NOW())
                """, (id, novo_total, oficina_id))
        else:
            # Se saiu de Finalizada, remove a receita vinculada a essa OS
            cursor.execute("""
                DELETE FROM financeiro
                WHERE ordem_servico_id = %s AND tipo = 'Receita' AND oficina_id = %s
            """, (id, oficina_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"msg": "Ordem atualizada com sucesso"})
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Erro ao editar ordem de serviço: {str(e)}")
        return jsonify({"erro": str(e)}), 500

# =====================================================
# DELETAR ORDEM DE SERVIÇO (VALIDAR OFICINA_ID)
# =====================================================
@dashboard_bp.route("/ordens-servico/<int:id>", methods=["DELETE"])
def deletar_ordem_servico(id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # verifica se tem financeiro
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM financeiro
        WHERE ordem_servico_id = %s AND oficina_id = %s
    """, (id, oficina_id))
    resultado = cursor.fetchone()

    if resultado["total"] > 0:
        cursor.close()
        conn.close()
        return jsonify({
            "erro": "Esta OS possui movimentação financeira e não pode ser excluída."
        }), 400

    # se não tiver, pode excluir
    cursor.execute("DELETE FROM ordem_servico_servicos WHERE ordem_servico_id = %s", (id,))
    cursor.execute("""
        DELETE FROM ordens_servico 
        WHERE id = %s AND oficina_id = %s
    """, (id, oficina_id))
    conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"msg": "Ordem excluída com sucesso"})

# =====================================================
# SERVIÇOS (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/servicos/list", methods=["GET"])
def listar_servicos_completo():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, nome, categoria, tempo_estimado, preco_base, status
        FROM servicos
        WHERE oficina_id = %s
        ORDER BY nome
    """, (oficina_id,))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(dados)

@dashboard_bp.route("/servicos/list", methods=["POST"])
def criar_servico():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        categoria = data.get("categoria", "")
        tempo_estimado = data.get("tempo_estimado")
        preco_base = data.get("preco_base")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")
        
        if not nome:
            return jsonify({"erro": "Nome do serviço é obrigatório"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        cursor.execute("""
            INSERT INTO servicos (nome, categoria, tempo_estimado, preco_base, status, oficina_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, categoria, tempo_estimado, preco_base, status, oficina_id))
        
        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Serviço criado com sucesso", "servico_id": novo_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/servicos/list/<int:servico_id>", methods=["PUT"])
def editar_servico(servico_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        categoria = data.get("categoria", "")
        tempo_estimado = data.get("tempo_estimado")
        preco_base = data.get("preco_base")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        cursor.execute("""
            UPDATE servicos
            SET nome = %s, categoria = %s, tempo_estimado = %s, preco_base = %s, status = %s
            WHERE id = %s AND oficina_id = %s
        """, (nome, categoria, tempo_estimado, preco_base, status, servico_id, oficina_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Serviço atualizado com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/servicos/list/<int:servico_id>", methods=["DELETE"])
def deletar_servico(servico_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT COUNT(*) AS total FROM ordem_servico_servicos 
            WHERE servico_id = %s
        """, (servico_id,))
        resultado = cursor.fetchone()
        if resultado and resultado.get("total", 0) > 0:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Não é possível excluir serviço vinculado a ordens"}), 400
        
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM servicos 
            WHERE id = %s AND oficina_id = %s
        """, (servico_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Serviço excluído com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# PEÇAS (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/pecas", methods=["GET"])
def listar_pecas():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, nome, codigo, quantidade, minimo, preco_unitario, status
        FROM pecas
        WHERE oficina_id = %s
        ORDER BY nome
    """, (oficina_id,))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(dados)

@dashboard_bp.route("/pecas", methods=["POST"])
def criar_peca():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        codigo = data.get("codigo", "")
        quantidade = data.get("quantidade", 0)
        minimo = data.get("minimo", 0)
        preco_unitario = data.get("preco_unitario", 0)
        oficina_id = data.get("oficina_id")
        
        # Calcular status baseado na quantidade
        if quantidade == 0:
            status = "Sem Estoque"
        elif quantidade <= minimo:
            status = "Baixo"
        else:
            status = "Em Estoque"
        
        if not nome or not codigo:
            return jsonify({"erro": "Nome e código são obrigatórios"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        cursor.execute("""
            INSERT INTO pecas (nome, codigo, quantidade, minimo, preco_unitario, status, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (nome, codigo, quantidade, minimo, preco_unitario, status, oficina_id))
        
        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Peça criada com sucesso", "peca_id": novo_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/pecas/<int:peca_id>", methods=["PUT"])
def editar_peca(peca_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        codigo = data.get("codigo", "")
        quantidade = data.get("quantidade", 0)
        minimo = data.get("minimo", 0)
        preco_unitario = data.get("preco_unitario", 0)
        oficina_id = data.get("oficina_id")
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        # Calcular status baseado na quantidade
        if quantidade == 0:
            status = "Sem Estoque"
        elif quantidade <= minimo:
            status = "Baixo"
        else:
            status = "Em Estoque"
        
        cursor.execute("""
            UPDATE pecas
            SET nome = %s, codigo = %s, quantidade = %s, minimo = %s, preco_unitario = %s, status = %s
            WHERE id = %s AND oficina_id = %s
        """, (nome, codigo, quantidade, minimo, preco_unitario, status, peca_id, oficina_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Peça atualizada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/pecas/<int:peca_id>", methods=["DELETE"])
def deletar_peca(peca_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM pecas 
            WHERE id = %s AND oficina_id = %s
        """, (peca_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Peça excluída com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# FINANCEIRO (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/financeiro", methods=["GET"])
def listar_financeiro():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            f.id, 
            f.ordem_servico_id, 
            f.tipo, 
            f.valor, 
            COALESCE(f.descricao, GROUP_CONCAT(DISTINCT s.nome SEPARATOR ', ')) as descricao,
            f.created_at
        FROM financeiro f
        LEFT JOIN ordens_servico os ON f.ordem_servico_id = os.id AND os.oficina_id = %s
        LEFT JOIN ordem_servico_servicos oss ON oss.ordem_servico_id = os.id
        LEFT JOIN servicos s ON s.id = oss.servico_id AND s.oficina_id = %s
        WHERE f.oficina_id = %s
        GROUP BY f.id, f.ordem_servico_id, f.tipo, f.valor, f.created_at
        ORDER BY f.created_at DESC
        LIMIT 100
    """, (oficina_id, oficina_id, oficina_id))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(dados)

@dashboard_bp.route("/financeiro/resumo", methods=["GET"])
def resumo_financeiro():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo='Receita' THEN valor ELSE 0 END), 0) AS receita,
            COALESCE(SUM(CASE WHEN tipo='Despesa' THEN valor ELSE 0 END), 0) AS despesa
        FROM financeiro
        WHERE oficina_id = %s
    """, (oficina_id,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    
    receita = resultado.get("receita", 0) if resultado else 0
    despesa = resultado.get("despesa", 0) if resultado else 0
    lucro = receita - despesa
    
    return jsonify({
        "receita": receita,
        "despesa": despesa,
        "lucro": lucro,
        "lucratividade": ((lucro / receita * 100) if receita > 0 else 0)
    })

@dashboard_bp.route("/financeiro", methods=["POST"])
def criar_financeiro():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        ordem_servico_id = data.get("ordem_servico_id", None)
        tipo = data.get("tipo", "Receita")
        valor = data.get("valor", 0)
        descricao = data.get("descricao", "")
        oficina_id = data.get("oficina_id")
        
        if not tipo or not valor:
            return jsonify({"erro": "Tipo e valor são obrigatórios"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        # Se for DESPESA vinculada a uma OS finalizada, bloquear
        if tipo == "Despesa" and ordem_servico_id is not None:
            cursor.execute("""
                SELECT status FROM ordens_servico 
                WHERE id = %s AND oficina_id = %s
            """, (ordem_servico_id, oficina_id))
            os_row = cursor.fetchone()
            if not os_row:
                return jsonify({"erro": "Ordem de serviço não encontrada"}), 404
            if str(os_row.get("status", "")).lower() == "finalizada":
                return jsonify({"erro": "Não é permitido vincular despesa a OS finalizada"}), 400
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro (ordem_servico_id, tipo, valor, descricao, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (ordem_servico_id, tipo, valor, descricao, oficina_id))
        
        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Transação criada com sucesso", "financeiro_id": novo_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/financeiro/<int:financeiro_id>", methods=["PUT"])
def editar_financeiro(financeiro_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        oficina_id = data.get("oficina_id")
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        # Buscar transação atual
        cursor.execute("""
            SELECT id, ordem_servico_id, tipo, valor, descricao
            FROM financeiro
            WHERE id = %s AND oficina_id = %s
        """, (financeiro_id, oficina_id))
        atual = cursor.fetchone()
        if not atual:
            cursor.close()
            conn.close()
            return jsonify({"erro": "Transação não encontrada"}), 404

        # Se for receita vinculada a OS, não permitir alterar valor/tipo/ordem_servico_id
        if (atual.get("tipo") == "Receita") and (atual.get("ordem_servico_id") is not None):
            os_id = atual.get("ordem_servico_id")
            # Garantir que o valor permaneça o total da OS
            cursor.execute("""
                SELECT total FROM ordens_servico 
                WHERE id = %s AND oficina_id = %s
            """, (os_id, oficina_id))
            os_row = cursor.fetchone()
            os_total = float(os_row.get("total", 0)) if os_row else 0.0

            # Atualizar apenas a descrição; manter valor/tipo/ordem_servico_id consistentes
            descricao = data.get("descricao", atual.get("descricao", ""))

            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE financeiro
                SET descricao = %s, valor = %s
                WHERE id = %s AND oficina_id = %s
                """,
                (descricao, os_total, financeiro_id, oficina_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"msg": "Transação vinculada a OS; valor controlado pela OS"}), 200

        # Caso contrário, permitir atualização normal
        ordem_servico_id = data.get("ordem_servico_id", None)
        tipo = data.get("tipo", atual.get("tipo", "Receita"))
        valor = data.get("valor", atual.get("valor", 0))
        descricao = data.get("descricao", atual.get("descricao", ""))

        # Se for DESPESA vinculada a uma OS finalizada, bloquear
        if tipo == "Despesa" and ordem_servico_id is not None:
            cursor.execute("""
                SELECT status FROM ordens_servico 
                WHERE id = %s AND oficina_id = %s
            """, (ordem_servico_id, oficina_id))
            os_row = cursor.fetchone()
            if not os_row:
                cursor.close(); conn.close()
                return jsonify({"erro": "Ordem de serviço não encontrada"}), 404
            if str(os_row.get("status", "")).lower() == "finalizada":
                cursor.close(); conn.close()
                return jsonify({"erro": "Não é permitido vincular despesa a OS finalizada"}), 400

        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE financeiro
            SET ordem_servico_id = %s, tipo = %s, valor = %s, descricao = %s
            WHERE id = %s AND oficina_id = %s
            """,
            (ordem_servico_id, tipo, valor, descricao, financeiro_id, oficina_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"msg": "Transação atualizada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/financeiro/<int:financeiro_id>", methods=["DELETE"])
def deletar_financeiro(financeiro_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM financeiro 
            WHERE id = %s AND oficina_id = %s
        """, (financeiro_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Transação deletada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

# =====================================================
# DASHBOARD (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard():
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    mes = request.args.get("mes")
    ano = request.args.get("ano")

    if mes and ano:
        filtro_mes = int(mes)
        filtro_ano = int(ano)
    else:
        hoje = datetime.now()
        filtro_mes = hoje.month
        filtro_ano = hoje.year

    # =========================
    # ORDENS DE SERVIÇO
    # =========================
    cursor.execute("""
        SELECT
            os.id AS ordem_id,
            os.status,
            os.total,
            os.observacao,
            c.nome AS nome_cliente,
            v.marca AS marca_veiculo,
            v.modelo AS modelo_veiculo
        FROM ordens_servico os
        JOIN clientes c ON c.id = os.cliente_id AND c.oficina_id = %s
        JOIN veiculos v ON v.id = os.veiculo_id AND v.oficina_id = %s
        WHERE os.oficina_id = %s
        GROUP BY os.id, os.status, os.total, os.observacao, c.nome, v.marca, v.modelo, os.created_at
        ORDER BY os.created_at DESC;
    """, (oficina_id, oficina_id, oficina_id))
    ordens_servico = cursor.fetchall()

    # =========================
    # PEÇAS / ESTOQUE
    # =========================
    cursor.execute("""
        SELECT 
            p.id,
            p.nome,
            p.quantidade,
            p.status,
            p.preco_unitario
        FROM pecas p
        WHERE p.oficina_id = %s
    """, (oficina_id,))
    pecas = cursor.fetchall()

    # =========================
    # RESUMO FINANCEIRO MENSAL (CORRIGIDO)
    # =========================
    # Somar entradas e despesas do financeiro
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo='Receita' THEN valor ELSE 0 END),0) AS entrada,
            COALESCE(SUM(CASE WHEN tipo='Despesa' THEN valor ELSE 0 END),0) AS saida
        FROM financeiro
        WHERE MONTH(created_at) = %s
        AND YEAR(created_at) = %s
        AND oficina_id = %s
    """, (filtro_mes, filtro_ano, oficina_id))

    resumo_financeiro = cursor.fetchone() or {}
    entrada = resumo_financeiro["entrada"]
    saida = resumo_financeiro["saida"]
    saldo = entrada - saida

    # =========================
    # MOVIMENTAÇÃO MENSAL (GRÁFICO)
    # =========================
    cursor.execute("""
        SELECT
            YEAR(created_at) AS ano,
            MONTH(created_at) AS mes,
            SUM(CASE WHEN tipo = 'Receita' THEN valor ELSE 0 END) AS entradas,
            SUM(CASE WHEN tipo = 'Despesa' THEN valor ELSE 0 END) AS saidas
        FROM financeiro
        WHERE oficina_id = %s
        GROUP BY YEAR(created_at), MONTH(created_at)
        ORDER BY ano, mes
    """, (oficina_id,))
    movimentacao_mensal = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "ordens_servico": ordens_servico,
        "pecas": pecas,
        "movimentacao_mensal": movimentacao_mensal,
        "resumo_mensal": {
            "entrada": entrada,
            "saida": saida,
            "saldo": saldo
        }
    })

# =====================================================
# USUÁRIOS (COM FILTRO DE OFICINA)
# =====================================================
@dashboard_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    oficina_id = request.args.get("oficina_id")
    
    # Se não tem oficina_id, retorna todos usuários (para tela de login)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if oficina_id:
        cursor.execute("""
            SELECT id, nome, email, cargo, departamento, status, created_at, oficina_id
            FROM usuarios
            WHERE oficina_id = %s
            ORDER BY nome
        """, (oficina_id,))
    else:
        # Para tela de login - retorna todos usuários ativos
        cursor.execute("""
            SELECT id, nome, email, cargo, departamento, status, created_at, oficina_id
            FROM usuarios
            WHERE status = 'Ativo'
            ORDER BY nome
        """)
    
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(dados)

@dashboard_bp.route("/login", methods=["POST"])
def login_usuario():
    data = request.json
    email = data.get("email", "")
    senha = data.get("senha", "")
    
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.cargo, u.departamento, u.status, u.senha, u.oficina_id, o.nome AS oficina_nome
            FROM usuarios u
            LEFT JOIN oficinas o ON u.oficina_id = o.id
            WHERE u.email = %s AND u.status = 'Ativo'
        """, (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Verificar senha com bcrypt
        if not verify_password(senha, usuario['senha']):
            return jsonify({"erro": "Senha incorreta"}), 401
        
        # Remove senha da resposta
        del usuario['senha']
        
        return jsonify({"msg": "Login bem-sucedido", "usuario": usuario}), 200
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        email = data.get("email", "")
        cargo = data.get("cargo", "")
        departamento = data.get("departamento", "")
        senha = data.get("senha", "")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")
        
        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        # Hash da senha com bcrypt
        senha_hash = hash_password(senha)
        
        cursor.execute("""
            INSERT INTO usuarios (nome, email, cargo, departamento, senha, status, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (nome, email, cargo, departamento, senha_hash, status, oficina_id))
        
        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Usuário criado com sucesso", "usuario_id": novo_id}), 201
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/usuarios/<int:usuario_id>", methods=["PUT"])
def editar_usuario(usuario_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        nome = data.get("nome", "")
        email = data.get("email", "")
        cargo = data.get("cargo", "")
        departamento = data.get("departamento", "")
        senha = data.get("senha", "")
        status = data.get("status", "Ativo")
        oficina_id = data.get("oficina_id")
        
        if not oficina_id:
            return jsonify({"erro": "oficina_id é obrigatório"}), 400
        
        # Se senha foi fornecida, fazer hash
        if senha:
            senha_hash = hash_password(senha)
        else:
            # Se não foi fornecida, manter a existente
            cursor_check = conn.cursor(dictionary=True)
            cursor_check.execute("SELECT senha FROM usuarios WHERE id = %s", (usuario_id,))
            usuario_atual = cursor_check.fetchone()
            cursor_check.close()
            senha_hash = usuario_atual['senha'] if usuario_atual else ""
        
        cursor.execute("""
            UPDATE usuarios
            SET nome = %s, email = %s, cargo = %s, departamento = %s, senha = %s, status = %s
            WHERE id = %s AND oficina_id = %s
        """, (nome, email, cargo, departamento, senha_hash, status, usuario_id, oficina_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Usuário atualizado com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400

@dashboard_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
def deletar_usuario(usuario_id):
    oficina_id = request.args.get("oficina_id")
    
    if not oficina_id:
        return jsonify({"erro": "oficina_id é obrigatório"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM usuarios 
            WHERE id = %s AND oficina_id = %s
        """, (usuario_id, oficina_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"msg": "Usuário excluído com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"erro": str(e)}), 400
