"""
Bionomia Name Normalization - Simple single function
"""
import requests
import json
from difflib import SequenceMatcher
from src.log import logger


def normalize_name(name, threshold=0.7, timeout=10):
    """
    Normalize a collector/determiner name using Bionomia API.

    Args:
        name: The name to normalize
        threshold: Minimum similarity threshold (0-1), default 0.7
        timeout: Request timeout in seconds, default 10
    """
    # Validate input
    if len(name.strip()) < 3:
        return {
            "status": "error",
            "original": name,
            "error": "Query too short (min 3 chars)",
        }

    try:
        # Search Bionomia API
        response = requests.get(
            "https://api.bionomia.net/user.json",
            params={"q": name, "has_occurrences": "true"},
            timeout=timeout,
        )
        response.raise_for_status()
        candidates = response.json()
        logger.info(f"Found {len(candidates)} possible bionomia candidates")
        if not candidates:
            return {"status": "not_found", "original": name}

        # Score each candidate name (by similarity)
        scored = []
        for candidate in candidates:
            similarity = _calculate_similarity(name, candidate)
            if similarity >= threshold:
                alternate_names = []
                if candidate.get("fullname"):
                    alternate_names.append(candidate.get("fullname"))
                if candidate.get("fullname_reverse"):
                    alternate_names.append(candidate.get("fullname_reverse"))
                if candidate.get("other_names"):
                    alternate_names.extend(candidate.get("other_names"))
                scored.append({"similarity": similarity, "data": candidate, "all_names": alternate_names})

        if not scored:
            return {
                "status": "no_good_match",
                "original": name,
                "found_count": len(candidates),
                "threshold": threshold,
            }

        # Sort by similarity
        best_match = sorted(scored, key=lambda x: x["similarity"], reverse=True)[0]
        d = best_match["data"].copy()
        d["status"] = "found"
        d["original"] = name
        d["all_names"] = best_match["all_names"]
        d["similarity"] = best_match["similarity"]
        return d

    except requests.exceptions.RequestException as e:
        return {"status": "error", "original": name, "error": str(e)}


def _calculate_similarity(query, candidate):
    """
    Calculate a similarity score between the input query and a Bionomia candidate record.

    Author names may be represented in multiple, highly variable ways (e.g. initials, name inversion, abbreviations).
    To ensure robust matching, this function compares the query string to every available name form associated 
    with the candidate record (including full name, label, reverse form, and any aliases in 'other_names').
    
    The function evaluates similarity using several metrics:
      - Character-level similarity: How closely the processed query matches each candidate name as a string.
      - Token overlap: The proportion of shared name tokens (words/initials) between the query and each candidate name.
      - Substring presence: How many parts (tokens) of the query occur as substrings in each candidate name.

    For example, if the query is "J.D. Hooker" and a candidate record's full name is "Joseph Dalton Hooker", 
    character-level similarity alone yields a low score. However, if "J.D. Hooker" appears as an alias in 'other_names',
    the resulting score will reflect a near-exact match.

    The function returns the highest similarity score among all name variants associated with the candidate record.
    """
    def normalize_name(name):
        # Normalize names: replace punctuation with spaces, then normalize whitespace
        return " ".join(name.lower().replace(",", " ").replace(".", " ").split()).strip()
    
    query_clean = normalize_name(query)
    query_tokens = set(query_clean)

    candidate_names = [
        candidate.get("fullname", ""),
        candidate.get("label", ""),
        candidate.get("fullname_reverse", ""),
    ] + candidate.get("other_names", [])

    best_score = 0
    for cand_name in candidate_names:
        if not cand_name:
            continue

        cand_clean = normalize_name(cand_name)
        cand_tokens = set(cand_clean)

        # Token overlap (Jaccard)
        token_sim = (
            len(query_tokens & cand_tokens) / len(query_tokens | cand_tokens)
            if query_tokens and cand_tokens
            else 0
        )

        # Character similarity (difflib)
        char_sim = SequenceMatcher(None, query_clean, cand_clean).ratio()

        # Substring presence
        substring_sim = (
            sum(1 for t in query_tokens if t in cand_clean) / len(query_tokens)
            if query_tokens
            else 0
        )

        # Weighted combination
        combined = char_sim * 0.3 + token_sim * 0.4 + substring_sim * 0.3
        best_score = max(best_score, combined)

    return best_score


if __name__ == "__main__":
    result = normalize_name("J.D. Hooker")
    print(json.dumps(result, indent=4))
