#!/usr/bin/env python3
"""
Script para migrar senhas antigas em texto plano para hash bcrypt.
Execute apenas uma vez após implementar a segurança!
"""

import bcrypt
import mysql.connector
from connection import get_connection

def migrate_passwords():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar todos os usuários com senhas em texto plano (não começam com $2b$)
        cursor.execute("SELECT id, senha FROM usuarios WHERE senha NOT LIKE '$2b$%'")
        usuarios_com_senha_plana = cursor.fetchall()
        
        if not usuarios_com_senha_plana:
            print("✓ Todas as senhas já estão em hash!")
            cursor.close()
            conn.close()
            return
        
        print(f"Encontrados {len(usuarios_com_senha_plana)} usuários com senhas em texto plano")
        print("Iniciando migração...\n")
        
        # Migrar cada senha
        for usuario in usuarios_com_senha_plana:
            usuario_id = usuario['id']
            senha_plana = usuario['senha']
            
            # Gerar hash da senha em texto plano
            senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Atualizar no banco
            cursor.execute(
                "UPDATE usuarios SET senha = %s WHERE id = %s",
                (senha_hash, usuario_id)
            )
            
            print(f"✓ Usuário ID {usuario_id} - Senha migrada")
        
        conn.commit()
        print(f"\n✓ Migração concluída! {len(usuarios_com_senha_plana)} senhas foram hasheadas")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Erro durante migração: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO DE SENHAS - De Texto Plano para Hash Bcrypt")
    print("=" * 60 + "\n")
    
    confirmacao = input("Deseja continuar? (Digite 'SIM' para confirmar): ")
    
    if confirmacao.upper() == "SIM":
        migrate_passwords()
    else:
        print("Migração cancelada.")
