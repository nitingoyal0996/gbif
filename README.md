# GBIF Agent Project Architecture


## High-level

```mermaid
sequenceDiagram
    participant u as iChatBio
    participant e as Entrypoint - GBIF Agent
    participant p as Request Parser
    participant o as OpenAI API
    participant gb as GBIF API

    u->>e: makes request
    e->>p: parses request
    p->>o: llm processing
    o->>p: structured parameters
    p->>e: validated parameters
    e->>e: builds gbif request uri
    e->>gb: request
    gb->>e: response
    e->>e: generate artifacts
    e->>u: finishes request
```

## Entry Points Overview

1. **find_occurrence_records**: Search for species occurrence records
2. **count_occurrence_records**: Count occurrence records with faceted results
3. **find_species_records**: Search for species records
4. **count_species_records**: Count species records with faceted results
5. **find_species_taxonomic_information**: Retrieve comprehensive taxonomic information 