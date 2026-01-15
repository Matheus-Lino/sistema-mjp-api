from connection import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# Buscar OSs finalizadas sem receita no financeiro
cursor.execute('''
    SELECT 
        os.id, 
        c.nome AS cliente,
        v.marca, v.modelo,
        os.total,
        os.created_at
    FROM ordens_servico os
    LEFT JOIN clientes c ON os.cliente_id = c.id
    LEFT JOIN veiculos v ON os.veiculo_id = v.id
    LEFT JOIN financeiro f ON os.id = f.ordem_servico_id AND f.tipo = "Receita"
    WHERE os.status = 'Finalizada' AND f.id IS NULL
    ORDER BY os.id DESC
''')

dados = cursor.fetchall()
cursor.close()
conn.close()

if dados:
    print('OSs FINALIZADAS SEM LANÇAMENTO FINANCEIRO:')
    print('=' * 60)
    for os in dados:
        print(f"OS {os['id']}: {os['cliente']} - {os['marca']} {os['modelo']} - R$ {os['total']:.2f}")
else:
    print('Nenhuma OS finalizada sem lançamento financeiro encontrada')
