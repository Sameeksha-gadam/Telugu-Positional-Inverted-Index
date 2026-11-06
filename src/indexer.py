
import os
import sqlite3
import json
from preprocessing import preprocess_document, get_positions


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dataset_folder = os.path.join(project_folder, "dataset", "extracted_articles")
index_folder = os.path.join(project_folder, "index")

database_path = os.path.join(index_folder, "positional_index.db")


def create_index():

    os.makedirs(index_folder, exist_ok=True)

    if os.path.exists(database_path):
        os.remove(database_path)

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE vocabulary (
            term TEXT PRIMARY KEY,
            df INTEGER,
            cf INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE postings (
            term TEXT,
            document_id TEXT,
            positions TEXT,
            PRIMARY KEY (term, document_id)
        )
    """)

    files = sorted(
        [file for file in os.listdir(dataset_folder) if file.endswith(".txt")],
        key=lambda name: int(name[1:-4]) if name[1:-4].isdigit() else 0
    )

    vocabulary = {}

    print("Building positional index...")
    print("Total documents:", len(files))

    for file_name in files:

        file_path = os.path.join(dataset_folder, file_name)
        document_id = os.path.splitext(file_name)[0]

        words = preprocess_document(file_path)
        positions = get_positions(words)

        for term, term_positions in positions.items():

            if term not in vocabulary:
                vocabulary[term] = {"df": 0, "cf": 0}

            vocabulary[term]["df"] += 1
            vocabulary[term]["cf"] += len(term_positions)

            cursor.execute(
                "INSERT INTO postings VALUES (?, ?, ?)",
                (term, document_id, json.dumps(term_positions, ensure_ascii=False))
            )

        if len(vocabulary) % 1000 == 0:
            connection.commit()

        if int(document_id[1:]) % 50 == 0:
            print("Processed:", document_id)

    for term, values in vocabulary.items():

        cursor.execute(
            "INSERT INTO vocabulary VALUES (?, ?, ?)",
            (term, values["df"], values["cf"])
        )

    connection.commit()
    connection.close()

    print("\nIndexing completed!")
    print("Total documents:", len(files))
    print("Total unique terms:", len(vocabulary))
    print("Database saved at:", database_path)


if __name__ == "__main__":
    create_index()
