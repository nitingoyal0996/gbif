"""
GADM Geographic Address Resolution

Resolves hierarchical location addresses to GADM IDs for precise geographic filtering.

Example:
    location = Location(
        country="USA",
        state="Florida",
        county="Alachua"
    )

    gadm_id = resolve_to_gadm(location)
    # Returns: "USA.11.1_1" (Alachua County, Florida)
"""

import os
import sqlite3
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, Field
from src.models.location import Location

# Path to GADM GeoPackage
HERE = os.path.dirname(os.path.abspath(__file__))
GADM_GPKG_PATH = os.path.join(HERE, "gadm404.gpkg")


class GADMMatch(BaseModel):
    """Result from GADM resolution"""

    gid: str = Field(description="GADM ID (e.g., 'USA.11.1_1')")
    level: int = Field(
        description="GADM level (0=country, 1=state, 2=county, 3=locality)"
    )
    matched_name: str = Field(description="The place name that was matched")
    canonical_name: str = Field(description="Canonical name from GADM")
    hierarchy: Dict[str, str] = Field(
        description="Full hierarchy (level_0: 'USA', level_1: 'Florida', ...)"
    )
    resolution_trace: List[str] = Field(
        default_factory=list,
        description="Step-by-step trace of how this location was resolved"
    )


def _get_connection(trace: bool = False) -> sqlite3.Connection:
    """Open read-only connection to GADM GeoPackage"""
    if not os.path.exists(GADM_GPKG_PATH):
        raise FileNotFoundError(f"GADM file not found: {GADM_GPKG_PATH}")

    conn = sqlite3.connect(f"file:{GADM_GPKG_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    if trace:
        conn.set_trace_callback(print)

    return conn


def _get_layers(conn: sqlite3.Connection) -> List[str]:
    """Get feature table names from GeoPackage"""
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM gpkg_contents WHERE data_type = 'features'")
    return [row[0] for row in cur.fetchall()]


def _get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """Get column names for a table"""
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cur.fetchall()]


def _build_name_predicate(
    level: int, place_name: str, cols: List[str]
) -> Tuple[str, List[str]]:
    """
    Build SQL predicate for matching place name at a specific GADM level.

    Checks NAME_n, VARNAME_n, NL_NAME_n columns for that level.
    Uses exact (case-insensitive) matching only.
    """
    name_cols = [
        c
        for c in cols
        if c in [f"NAME_{level}", f"VARNAME_{level}", f"NL_NAME_{level}"]
    ]

    if not name_cols:
        return "1=0", []  # No name columns for this level

    predicates = [f'UPPER("{col}") = UPPER(?)' for col in name_cols]
    params = [place_name] * len(name_cols)

    return f"({' OR '.join(predicates)})", params


def _extract_hierarchy(row: sqlite3.Row) -> Dict[str, str]:
    """Extract full hierarchy from a GADM row"""
    row_dict = dict(row)
    hier = {}
    for level in range(5):
        name = row_dict.get(f"NAME_{level}")
        if name:
            hier[f"level_{level}"] = name
    return hier


def _search_at_level(
    conn: sqlite3.Connection,
    layer: str,
    level: int,
    place_name: str,
    parent_gid: Optional[str] = None,
    query_trace: Optional[List[str]] = None,
) -> Optional[GADMMatch]:
    """
    Search for a place at a specific GADM level.
    
    Uses exact name matching and optional parent GID constraint.
    
    Args:
        conn: Database connection
        layer: GADM layer name
        level: GADM level (0=country, 1=state, 2=county, 3=locality)
        place_name: Name to search for
        parent_gid: Optional parent's GID for exact hierarchical constraint
        query_trace: Optional list to append SQL queries to
        
    Returns:
        GADMMatch if found, None otherwise
    """
    cols = _get_columns(conn, layer)

    # Build name predicate (exact match only)
    name_clause, name_params = _build_name_predicate(level, place_name, cols)
    
    if name_clause == "1=0":
        return None

    # Build parent GID constraint (exact match)
    if parent_gid and level > 0:
        parent_col = f"GID_{level - 1}"
        if parent_col in cols:
            parent_clause = f'"{parent_col}" = ?'
            parent_params = [parent_gid]
        else:
            # Parent column doesn't exist in this layer
            return None
    else:
        parent_clause = "1=1"
        parent_params = []

    # Combine predicates
    where_sql = f"{name_clause} AND {parent_clause}"
    sql = f'SELECT * FROM "{layer}" WHERE {where_sql} LIMIT 1'
    params = name_params + parent_params

    # Log query with parameters
    if query_trace is not None:
        # Format query with parameters for readability
        query_str = sql
        for param in params:
            query_str = query_str.replace('?', f"'{param}'", 1)
        query_trace.append(query_str)

    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()

    if not row:
        return None

    row_dict = dict(row)
    gid = row_dict.get(f"GID_{level}")
    canonical_name = row_dict.get(f"NAME_{level}")
    hierarchy = _extract_hierarchy(row)

    if not gid:
        return None

    return GADMMatch(
        gid=gid,
        level=level,
        matched_name=place_name,
        canonical_name=canonical_name,
        hierarchy=hierarchy,
    )


def resolve_to_gadm(location: Location, trace: bool = False) -> Optional[GADMMatch]:
    """
    Resolve a location address to a GADM ID using recursive narrowing.
    
    Strategy:
        1. Start from least specific (country)
        2. Find exact match and get its GID
        3. Use that GID to constrain search at next level (state)
        4. Continue down the hierarchy until most specific level
        
    Example:
        Location(country="USA", state="Florida", county="Alachua")
        
        Step 1: Find USA → GID_0 = "USA"
        Step 2: Find Florida WHERE GID_0 = "USA" → GID_1 = "USA.11_1"
        Step 3: Find Alachua WHERE GID_1 = "USA.11_1" → GID_2 = "USA.11.1_1"
        
    Args:
        location: Location to resolve
        trace: Enable SQL query tracing to stderr (sqlite3 feature)
        
    Returns:
        GADMMatch with the most specific level found, or None if any level fails.
        The GADMMatch.resolution_trace contains all SQL queries executed.
    """
    conn = _get_connection(trace=trace)

    try:
        layers = _get_layers(conn)
        hierarchy = location.get_hierarchy()
        # for context logging
        resolution_trace = [] 

        if not hierarchy:
            return None

        # Reverse to go from least specific to most specific
        # Original: [(3, 'locality', 'X'), (2, 'county', 'Y'), (1, 'state', 'Z'), (0, 'country', 'W')]
        # Reversed: [(0, 'country', 'W'), (1, 'state', 'Z'), (2, 'county', 'Y'), (3, 'locality', 'X')]
        hierarchy = list(reversed(hierarchy))

        current_match = None
        current_gid = None

        # Narrow down the search by searching each level, using previous level's GID as constraint
        for level, level_name, place_name in hierarchy:
            if level_name == "continent":
                continue

            level_match = None

            # Try each layer until we find a match
            for layer in layers:
                match = _search_at_level(
                    conn, layer, level, place_name, parent_gid=current_gid, query_trace=resolution_trace
                )
                if match:
                    level_match = match
                    break

            if not level_match:
                # If any level in the chain fails, return the last successful match
                # (e.g., if county not found, return state match)
                if current_match:
                    current_match.resolution_trace = resolution_trace
                return current_match

            # Update for next iteration
            current_match = level_match
            current_gid = level_match.gid

        # Attach trace to final result
        if current_match:
            current_match.resolution_trace = resolution_trace

        return current_match

    finally:
        conn.close()


# Testing methods
if __name__ == "__main__":
    # Example 1: Simple state lookup
    print("Example 1: California")
    loc = Location(country="United States", country_iso="USA", state="California")
    match = resolve_to_gadm(loc)
    print(f"  GADM ID: {match.gid if match else 'Not found'}")
    if match and match.resolution_trace:
        print("  SQL Queries:")
        for query in match.resolution_trace:
            print(f"    {query}")
    print()

    # Example 2: County with state context (disambiguation)
    print("Example 2: Alachua County, Florida")
    loc = Location(country="United States", country_iso="USA", state="Florida", county="Alachua")
    match = resolve_to_gadm(loc)
    print(f"  GADM ID: {match.gid if match else 'Not found'}")
    print(f"  Canonical: {match.canonical_name if match else 'N/A'}")
    if match and match.resolution_trace:
        print("  SQL Queries:")
        for query in match.resolution_trace:
            print(f"    {query}")
    print()

    # Example 3: Ambiguous name (should fail without parent context)
    print("Example 3: Just 'Springfield' (ambiguous)")
    loc = Location(locality="Springfield")
    match = resolve_to_gadm(loc)
    print(f"  GADM ID: {match.gid if match else 'Not found (too ambiguous)'}")
    print()

    # Example 4: Springfield with state context (disambiguated)
    print("Example 4: Springfield, Illinois (disambiguated)")
    loc = Location(country="United States", country_iso="USA", state="Florida", locality="Springfield")
    match = resolve_to_gadm(loc)
    print(f"  GADM ID: {match.gid if match else 'Not found'}")
    if match and match.resolution_trace:
        print("  SQL Queries:")
        for query in match.resolution_trace:
            print(f"    {query}")
