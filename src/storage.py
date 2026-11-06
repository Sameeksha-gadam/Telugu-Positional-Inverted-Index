
import os
import json
import sqlite3


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_folder = os.path.join(project_folder, "index")

database_path = os.path.join(index_folder, "positional_index.db")
postings_path = os.path.join(index_folder, "postings.txt")
vocabulary_path = os.path.join(index_folder, "vocabulary.json")


def save_index():

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    vocabulary = {}

    terms = cursor.execute(
        "SELECT term, df, cf FROM vocabulary ORDER BY term"
    ).fetchall()

    with open(postings_path, "wb") as file:

        for term, df, cf in terms:

            postings = cursor.execute(
                """
                SELECT document_id, positions
                FROM postings
                WHERE term = ?
                ORDER BY CAST(SUBSTR(document_id, 2) AS INTEGER)
                """,
                (term,)
            ).fetchall()

            posting_data = []

            for document_id, positions in postings:
                posting_data.append({
                    "document_id": document_id,
                    "positions": json.loads(positions)
                })

            offset = file.tell()

            record = {
                "term": term,
                "postings": posting_data
            }

            data = json.dumps(
                record,
                ensure_ascii=False
            ).encode("utf-8")

            file.write(data + b"\n")

            vocabulary[term] = {
                "offset": offset,
                "df": df,
                "cf": cf
            }

    with open(vocabulary_path, "w", encoding="utf-8") as file:
        json.dump(
            vocabulary,
            file,
            ensure_ascii=False
        )

    connection.close()

    print("Index storage completed!")
    print("Total vocabulary terms:", len(vocabulary))
    print("Postings file:", postings_path)
    print("Vocabulary file:", vocabulary_path)


if __name__ == "__main__":
    save_index()
