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
    
    print("\n=== ATUALIZANDO ordem_servico_servicos ===\n")
    
    # Verificar se tabela existe
    cursor.execute("SHOW TABLES LIKE 'ordem_servico_servicos'")
    if not cursor.fetchone():
        print("❌ Tabela 'ordem_servico_servicos' não existe")
    else:
        # Verificar se coluna já existe
        cursor.execute("SHOW COLUMNS FROM ordem_servico_servicos LIKE 'oficina_id'")
        result = cursor.fetchone()
        
        if result:
            print("✅ 'ordem_servico_servicos' já tem oficina_id")
        else:
            # Adicionar coluna
            cursor.execute("ALTER TABLE ordem_servico_servicos ADD COLUMN oficina_id INT")
            print("✅ Coluna oficina_id adicionada em 'ordem_servico_servicos'")
            
            # Criar índice
            try:
                cursor.execute("CREATE INDEX idx_ordem_servico_servicos_oficina ON ordem_servico_servicos(oficina_id)")
                print("✅ Índice criado")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("✅ Índice já existe")
            
            # Pegar oficina_id padrão
            cursor.execute("SELECT id FROM oficinas LIMIT 1")
            oficina = cursor.fetchone()
            oficina_id = oficina[0] if oficina else 1
            
            # Atualizar registros existentes
            cursor.execute("UPDATE ordem_servico_servicos SET oficina_id = %s WHERE oficina_id IS NULL", (oficina_id,))
            rows = cursor.rowcount
            if rows > 0:
                print(f"✅ {rows} registros atualizados")
            
            conn.commit()
            print("\n✅ ATUALIZAÇÃO CONCLUÍDA!\n")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ ERRO: {e}\n")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
