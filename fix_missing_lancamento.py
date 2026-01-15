from connection import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# Buscar OSs finalizadas sem receita no financeiro
cursor.execute('''
    SELECT 
        os.id, 
        os.oficina_id,
        os.total
    FROM ordens_servico os
    LEFT JOIN financeiro f ON os.id = f.ordem_servico_id AND f.tipo = "Receita"
    WHERE os.status = 'Finalizada' AND f.id IS NULL
    ORDER BY os.id DESC
''')

dados = cursor.fetchall()

if dados:
    print('Lançando receitas para OSs finalizadas sem financeiro...')
    print('=' * 60)
    
    for os in dados:
        cursor.execute('''
            INSERT INTO financeiro
            (ordem_servico_id, tipo, valor, oficina_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        ''', (os['id'], 'Receita', os['total'], os['oficina_id']))
        
        conn.commit()
        print(f"✓ OS {os['id']}: Lançamento de R$ {os['total']:.2f} criado com sucesso")
    
    print('=' * 60)
    print(f'Total: {len(dados)} lançamento(s) criado(s)')
else:
    print('Nenhuma OS finalizada sem lançamento encontrada')

cursor.close()
conn.close()
