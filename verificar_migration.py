import mysql.connector

try:
    conn = mysql.connector.connect(
        user='root',
        password='Ponte123',
        host='localhost',
        database='oficina_mjp'
    )
    cursor = conn.cursor()
    
    print("\n=== VERIFICANDO TABELAS ===\n")
    
    # Verificar se tabela oficinas existe
    try:
        cursor.execute("SHOW COLUMNS FROM oficinas")
        print("✅ Tabela 'oficinas' existe")
        print("   Colunas:")
        for col in cursor.fetchall():
            print(f"   - {col[0]}")
    except Exception as e:
        print(f"❌ Tabela 'oficinas' NÃO existe: {e}")
    
    print()
    
    # Verificar coluna oficina_id em usuarios
    try:
        cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'oficina_id'")
        result = cursor.fetchone()
        if result:
            print("✅ Coluna 'oficina_id' existe em 'usuarios'")
        else:
            print("❌ Coluna 'oficina_id' NÃO existe em 'usuarios'")
    except Exception as e:
        print(f"❌ Erro ao verificar usuarios: {e}")
    
    # Verificar coluna oficina_id em clientes
    try:
        cursor.execute("SHOW COLUMNS FROM clientes LIKE 'oficina_id'")
        result = cursor.fetchone()
        if result:
            print("✅ Coluna 'oficina_id' existe em 'clientes'")
        else:
            print("❌ Coluna 'oficina_id' NÃO existe em 'clientes'")
    except Exception as e:
        print(f"❌ Erro ao verificar clientes: {e}")
    
    # Verificar coluna oficina_id em veiculos
    try:
        cursor.execute("SHOW COLUMNS FROM veiculos LIKE 'oficina_id'")
        result = cursor.fetchone()
        if result:
            print("✅ Coluna 'oficina_id' existe em 'veiculos'")
        else:
            print("❌ Coluna 'oficina_id' NÃO existe em 'veiculos'")
    except Exception as e:
        print(f"❌ Erro ao verificar veiculos: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===\n")

except Exception as e:
    print(f"❌ ERRO DE CONEXÃO: {e}")
