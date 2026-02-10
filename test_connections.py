#!/usr/bin/env python3
"""Test all database connections"""

import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))
URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AURA_USER = os.getenv('AURA_USER')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')

print("=" * 60)
print("TESTING ALL DATABASE CONNECTIONS")
print("=" * 60)

# Test MariaDB
print("\n1. Testing MariaDB...")
try:
    conn = mariadb.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, 
        database=DB_NAME, port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{DB_NAME}'")
    table_count = cursor.fetchone()[0]
    conn.close()
    print(f"   ✅ MariaDB Connected: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"   📊 Tables in database: {table_count}")
except Exception as e:
    print(f"   ❌ MariaDB Error: {e}")

# Test Neo4j
print("\n2. Testing Neo4j...")
try:
    with GraphDatabase.driver(URI, auth=(AURA_USER, AURA_PASSWORD)) as driver:
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
    print(f"   ✅ Neo4j Connected: {URI}")
    print(f"   📊 Total nodes: {node_count}")
except Exception as e:
    print(f"   ❌ Neo4j Error: {e}")

# Test Neo4j query
print("\n3. Testing Neo4j Query...")
try:
    with GraphDatabase.driver(URI, auth=(AURA_USER, AURA_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(*) as cnt ORDER BY cnt DESC LIMIT 5")
            records = [dict(r) for r in result]
    print("   Node types in graph:")
    for r in records:
        print(f"     - {r.get('label')}: {r.get('cnt')}")
    if not records:
        print("     (No nodes found - run Synthea pipeline to populate)")
except Exception as e:
    print(f"   ❌ Query Error: {e}")

# Test MariaDB query
print("\n4. Testing MariaDB Query...")
try:
    conn = mariadb.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, 
        database=DB_NAME, port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print("   Tables in database:")
    for t in tables[:10]:
        print(f"     - {t}")
    if len(tables) > 10:
        print(f"     ... and {len(tables)-10} more")
except Exception as e:
    print(f"   ❌ Query Error: {e}")

print("\n" + "=" * 60)
print("✅ CONNECTION TESTS COMPLETE")
print("=" * 60)
