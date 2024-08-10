Extract all visible text from the image and provide the data in Neo4j property graph format in a complete JSON format with the following structure:
{
    "equities": [
        {
            "name": "Session {session_number} - {session_title}",
            "label": "Session",
            "properties": { ... }
        },
        {
            "name": "{entity_name}",
            "label": "{entity_label}",
            "properties": { ... }
        },
        ...
    ],
    "relations": [
        {
            "label": "{relation_label}",
            "source_id": {source_entity_id},
            "target_id": {target_entity_id},
            "properties": { ... }
        },
        ...
    ]
}
Instructions:

Equities (Nodes):

Each session should be a separate node with its number and title combined in the name field (e.g., "Session 1 - Product Name & Manufacturer Information").
Each entity (product, manufacturer, ingredient, hazard, etc.) should be a separate node with relevant properties.
Include all details within the properties of the appropriate nodes (e.g., "Primary Routes of Entry" should be a property under "Session 3 - Hazards Identification").
Relations (Edges):

Use "CONTAINS" as the relationship label to denote that one node contains another (e.g., "Session 1" contains "Product Name").
Make sure the source and target IDs correspond to the correct nodes.
Formatting:

Use date format "YYYY-MM-DD" for any dates.
Accurately capture the structure and meaning of the content, especially for sections like tables and checkboxes.



Extract all visible text from the image and provide the data in Neo4j property graph format in a complete JSON format with the following structure:

json
复制代码
{
    "equities": [
        {
            "name": "Session {session_number} - {session_title}",
            "label": "Session",
            "properties": { ... }
        },
        {
            "name": "{entity_name}",
            "label": "{entity_label}",
            "properties": { ... }
        },
        ...
    ],
    "relations": [
        {
            "label": "{relation_label}",
            "source_id": {source_entity_id},
            "target_id": {target_entity_id},
            "properties": { ... }
        },
        ...
    ]
}
Instructions:

Equities (Nodes):

Each session should be a separate node with its number and title combined in the name field (e.g., "Session 1 - Product Information").
Each entity (e.g., product, manufacturer, ingredient, hazard, first aid measure, etc.) should be a separate node with relevant properties.
Specific details within sessions should be extended into separate nodes where applicable (e.g., "Emergency Overview," "Effects of Overexposure," "Medical Conditions Aggravated by Exposure" under a hazards session; "Skin Contact," "Eye Contact," "Inhalation," and "Ingestion" under a first aid session).
Relations (Edges):

Use "CONTAINS" as the relationship label to denote that one node contains another (e.g., a session node contains its related entities).
Make sure the source and target IDs correspond to the correct nodes.
Formatting:

Use date format "YYYY-MM-DD" for any dates.
Accurately capture the structure and meaning of the content, especially for sections like tables and checkboxes.

** for claude**
Extract all text from the image. provide every data in Neo4j property graph format in a complete JSON format with the following structure:
            {
                "Filename": "sheet.jpg",
                "Category": "Sheet",
                "Document": {
                    "Title": "data sheet",
                    "Equities": [
                        {
                            "name": "Section 1-Product Name & Manufacture Information",
                            "type": "Section",
                            "properties": { ... }
                        },
                        {
                            "name": "product name",
                            "type": "Name",
                            "properties": { ... }
                        },
                        ...
                    ],
                    "Relations": [
                        {
                            "source": "Section 1-Product Name & Manufacture Information",
                            "target": "product name",
                            "type": "HAS"
                        },
                        ...
                    ]
                }
            }

Instructions:
Equities (Nodes):
Each section should be a separate node with its number and title combined in the name field (e.g., "Section 1 - Product Name & Manufacturer Information").
Each entity (e.g., product, manufacturer, ingredient, hazard, first aid measure, etc.) should be a separate node with relevant properties.
Specific details within section should be extended into separate nodes where applicable (e.g., "Emergency Overview," "Effects of Overexposure," "Medical Conditions Aggravated by Exposure" under a hazards session; "Skin Contact," "Eye Contact," "Inhalation," and "Ingestion" under a first aid session).

Relations (Edges):
Use "HAS" as the relationship label to denote that one node contains another (e.g., a session node contains its related entities).
Make sure the source and target correspond to the correct nodes.

Formatting:
Use date format "YYYY-MM-DD" for any dates.
Accurately capture the structure and meaning of the content, especially for sections like tables and checkboxes.
