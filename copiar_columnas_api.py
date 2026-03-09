"""
Copia los valores de las columnas origen al board 'leads evaluaciones'
hacia las columnas API correspondientes.

Mapeo:
  INST FINANCIERA  → Inst Financiera API
  MAXIMO PUNTAJE   → Max Ptje API
  ESTADO ACTUAL    → Estado Actual API
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.monday.com/v2"
CONFIG_FILE = Path(__file__).parent / "config_columnas.json"


def get_headers():
    token = os.getenv("MONDAY_API_TOKEN")
    if not token:
        print("Error: Define MONDAY_API_TOKEN en el archivo .env")
        sys.exit(1)
    return {"Authorization": token, "Content-Type": "application/json"}


def load_mapping():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["mapeo_columnas"]


def run_graphql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(API_URL, json=payload, headers=get_headers())
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data.get("data", {})


def get_board_columns(board_id):
    """Obtiene todas las columnas del board con id y título."""
    query = """
    query ($boardId: ID!) {
      boards(ids: [$boardId]) {
        columns { id title type }
      }
    }
    """
    data = run_graphql(query, {"boardId": str(board_id)})
    boards = data.get("boards") or []
    if not boards:
        raise RuntimeError(f"No se encontró el board con ID {board_id}")
    return {col["title"].strip(): col for col in boards[0].get("columns", [])}


def get_items_with_columns(board_id, _column_ids):
    """Obtiene todos los ítems del board con los valores de todas las columnas."""
    query_first = """
    query ($boardId: ID!) {
      boards(ids: [$boardId]) {
        items_page(limit: 500) {
          cursor
          items {
            id
            name
            column_values {
              id
              title
              text
              type
              value
            }
          }
        }
      }
    }
    """
    query_next = """
    query ($cursor: String!) {
      next_items_page(cursor: $cursor) {
        cursor
        items {
          id
          name
          column_values {
            id
            title
            text
            type
            value
          }
        }
      }
    }
    """
    all_items = []
    cursor = None
    while True:
        if cursor is None:
            data = run_graphql(query_first, {"boardId": str(board_id)})
            boards = data.get("boards") or []
            if not boards:
                break
            page = boards[0].get("items_page") or {}
        else:
            data = run_graphql(query_next, {"cursor": cursor})
            page = data.get("next_items_page") or {}
        items = page.get("items") or []
        all_items.extend(items)
        cursor = page.get("cursor")
        if not cursor or not items:
            break
    return all_items


def copy_value_for_column(col_type, col_value):
    """Convierte el valor de origen al formato esperado por la columna destino (texto o número)."""
    if col_value is None or (isinstance(col_value, str) and col_value.strip() == ""):
        return ""
    # Para números, la API acepta string "123"
    if col_type == "numbers":
        s = str(col_value).strip()
        return s if s else ""
    # Texto y otros: pasar como string
    return str(col_value).strip()


def update_item_columns(board_id, item_id, column_values_dict):
    """Actualiza varias columnas de un ítem con change_multiple_column_values."""
    # La API espera valores según tipo: texto/número como string está bien
    values_json = json.dumps(column_values_dict)
    mutation = """
    mutation ($boardId: ID!, $itemId: ID!, $columnValues: JSON!) {
      change_multiple_column_values(board_id: $boardId, item_id: $itemId, column_values: $columnValues) {
        id
      }
    }
    """
    run_graphql(mutation, {
        "boardId": board_id,
        "itemId": item_id,
        "columnValues": values_json,
    })


def main():
    board_id = os.getenv("BOARD_ID")
    if not board_id:
        print("Error: Define BOARD_ID en el archivo .env (ID del board 'leads evaluaciones')")
        sys.exit(1)

    mapeo = load_mapping()
    # Todas las columnas que necesitamos (origen + destino)
    todas_las_columnas = set(mapeo.keys()) | set(mapeo.values())

    print("Obteniendo columnas del board...")
    columns_by_title = get_board_columns(board_id)
    missing = todas_las_columnas - set(columns_by_title.keys())
    if missing:
        print(f"Error: No se encontraron estas columnas en el board: {missing}")
        print("Columnas existentes:", list(columns_by_title.keys()))
        sys.exit(1)

    column_ids = [columns_by_title[t]["id"] for t in todas_las_columnas]
    print("Obteniendo ítems del board...")
    items = get_items_with_columns(board_id, column_ids)

    # Mapeo título -> id para las columnas destino
    dest_id_by_title = {t: columns_by_title[t]["id"] for t in mapeo.values()}
    actualizados = 0
    for item in items:
        col_vals = {cv["title"].strip(): cv for cv in item.get("column_values", [])}
        # Solo actualizar si algún valor de las 3 columnas origen es distinto al de la columna API
        hay_cambio = False
        updates = {}
        for titulo_origen, titulo_destino in mapeo.items():
            orig = col_vals.get(titulo_origen)
            dest = col_vals.get(titulo_destino)
            texto_origen = (orig.get("text") or "").strip() if orig else ""
            texto_destino = (dest.get("text") or "").strip() if dest else ""
            if texto_origen != texto_destino:
                hay_cambio = True
            dest_id = dest_id_by_title[titulo_destino]
            dest_type = columns_by_title[titulo_destino].get("type", "text")
            updates[dest_id] = copy_value_for_column(dest_type, texto_origen)
        if not hay_cambio:
            continue
        try:
            update_item_columns(board_id, item["id"], updates)
            actualizados += 1
            print(f"  Actualizado ítem: {item.get('name', item['id'])[:50]}")
        except Exception as e:
            print(f"  Error en ítem {item['id']}: {e}")

    print(f"\nListo. Se actualizaron {actualizados} ítem(s) (solo filas con cambios).")


if __name__ == "__main__":
    main()
