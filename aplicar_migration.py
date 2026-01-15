import mysql.connector

try:
    conn = mysql.connector.connect(
        user='root',
        password='Ponte123',
        host='localhost',
        database='oficina_mjp',
        autocommit=False
    )
    cursor = conn.cursor()
    
    print("\n=== APLICANDO MIGRATION - ADICIONANDO COLUNAS oficina_id ===\n")
    
    tabelas = ['usuarios', 'veiculos', 'servicos', 'pecas', 'ordens_servico', 'financeiro']
    
    for tabela in tabelas:
        try:
            # Verificar se coluna já existe
            cursor.execute(f"SHOW COLUMNS FROM {tabela} LIKE 'oficina_id'")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ '{tabela}' já tem oficina_id")
            else:
                # Adicionar coluna
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN oficina_id INT")
                print(f"✅ Coluna oficina_id adicionada em '{tabela}'")
        except Exception as e:
            print(f"❌ Erro em '{tabela}': {e}")
    
    print("\n=== CRIANDO ÍNDICES ===\n")
    
    for tabela in tabelas:
        try:
            cursor.execute(f"CREATE INDEX idx_{tabela}_oficina ON {tabela}(oficina_id)")
            print(f"✅ Índice criado em '{tabela}'")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print(f"✅ '{tabela}' já tem índice")
            else:
                print(f"⚠️ Aviso em '{tabela}': {e}")
    
    print("\n=== MIGRANDO DADOS EXISTENTES ===\n")
    
    # Verificar se já existe uma oficina
    cursor.execute("SELECT id FROM oficinas LIMIT 1")
    oficina = cursor.fetchone()
    
    if oficina:
        oficina_id = oficina[0]
        print(f"✅ Usando oficina_id = {oficina_id}")
    else:
        # Criar oficina padrão
        cursor.execute("""
            INSERT INTO oficinas (nome, cnpj, telefone, email) 
            VALUES ('Oficina Principal', '', '', '')
        """)
        oficina_id = cursor.lastrowid
        print(f"✅ Oficina padrão criada com id = {oficina_id}")
    
    # Atualizar registros sem oficina_id
    for tabela in tabelas:
        try:
            cursor.execute(f"UPDATE {tabela} SET oficina_id = %s WHERE oficina_id IS NULL", (oficina_id,))
            rows = cursor.rowcount
            if rows > 0:
                print(f"✅ {rows} registros atualizados em '{tabela}'")
            else:
                print(f"✅ '{tabela}' já está atualizada")
        except Exception as e:
            print(f"❌ Erro ao atualizar '{tabela}': {e}")
    
    # Commit das alterações
    conn.commit()
    print("\n✅ MIGRATION APLICADA COM SUCESSO!\n")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ ERRO: {e}\n")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
