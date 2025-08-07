#!/usr/bin/env python3
import psycopg2
import sys

def connect_db(host, database, user, password):
“”“Connexion à la base de données PostgreSQL”””
try:
conn = psycopg2.connect(
host=host,
database=database,
user=user,
password=password
)
return conn
except Exception as e:
print(f”Erreur de connexion: {e}”)
sys.exit(1)

def get_tables_and_columns(cursor):
“”“Récupère les tables et colonnes”””
query = “””
SELECT
t.table_name,
c.column_name,
c.data_type,
c.is_nullable,
CASE WHEN tc.constraint_type = ‘PRIMARY KEY’ THEN ‘PK’
WHEN tc.constraint_type = ‘UNIQUE’ THEN ‘UK’
ELSE ‘’
END as constraint_type
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
LEFT JOIN information_schema.key_column_usage kcu
ON c.table_name = kcu.table_name AND c.column_name = kcu.column_name
LEFT JOIN information_schema.table_constraints tc
ON kcu.constraint_name = tc.constraint_name
WHERE t.table_schema = ‘public’
AND t.table_type = ‘BASE TABLE’
ORDER BY t.table_name, c.ordinal_position;
“””
cursor.execute(query)
return cursor.fetchall()

def get_foreign_keys(cursor):
“”“Récupère les clés étrangères”””
query = “””
SELECT
tc.table_name,
kcu.column_name,
ccu.table_name AS foreign_table_name,
ccu.column_name AS foreign_column_name,
tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = ‘FOREIGN KEY’
AND tc.table_schema = ‘public’;
“””
cursor.execute(query)
return cursor.fetchall()

def map_data_type(pg_type):
“”“Convertit les types PostgreSQL vers des types Mermaid”””
type_mapping = {
‘integer’: ‘int’,
‘bigint’: ‘long’,
‘smallint’: ‘int’,
‘character varying’: ‘string’,
‘varchar’: ‘string’,
‘text’: ‘string’,
‘char’: ‘string’,
‘boolean’: ‘boolean’,
‘timestamp’: ‘datetime’,
‘timestamptz’: ‘datetime’,
‘date’: ‘date’,
‘time’: ‘time’,
‘decimal’: ‘decimal’,
‘numeric’: ‘decimal’,
‘real’: ‘float’,
‘double precision’: ‘double’,
‘uuid’: ‘string’,
‘json’: ‘json’,
‘jsonb’: ‘json’
}
return type_mapping.get(pg_type, pg_type)

def generate_mermaid_diagram(host, database, user, password):
“”“Génère le diagramme Mermaid”””
conn = connect_db(host, database, user, password)
cursor = conn.cursor()

```
# Récupération des données
tables_data = get_tables_and_columns(cursor)
foreign_keys = get_foreign_keys(cursor)

# Organisation des données par table
tables = {}
for row in tables_data:
    table_name, column_name, data_type, is_nullable, constraint_type = row
    if table_name not in tables:
        tables[table_name] = []
    
    # Formatage du type
    mermaid_type = map_data_type(data_type)
    
    # Ajout des contraintes
    constraints = []
    if constraint_type == 'PK':
        constraints.append('PK')
    if is_nullable == 'NO':
        constraints.append('NOT NULL')
        
    constraint_str = ' ' + ','.join(constraints) if constraints else ''
    
    tables[table_name].append(f"{column_name} {mermaid_type}{constraint_str}")

# Génération du diagramme Mermaid
print("erDiagram")
print()

# Entités
for table_name, columns in tables.items():
    print(f"    {table_name} {{")
    for column in columns:
        print(f"        {column}")
    print(f"    }}")
    print()

# Relations
relationships = set()  # Éviter les doublons
for fk in foreign_keys:
    source_table, source_column, target_table, target_column, constraint_name = fk
    # Format: TABLE1 ||--o{ TABLE2 : "relation_name"
    relationship = f"    {target_table} ||--o{{ {source_table} : \"{constraint_name}\""
    relationships.add(relationship)

for rel in sorted(relationships):
    print(rel)

cursor.close()
conn.close()
```

def main():
“”“Fonction principale”””
if len(sys.argv) != 5:
print(“Usage: python3 pg_to_mermaid.py <host> <database> <user> <password>”)
print(“Exemple: python3 pg_to_mermaid.py localhost mydb postgres mypassword”)
sys.exit(1)

```
host, database, user, password = sys.argv[1:5]
generate_mermaid_diagram(host, database, user, password)
```

if **name** == “**main**”:
main()
