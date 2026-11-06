
import os
import json


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_folder = os.path.join(project_folder, "index")

postings_path = os.path.join(index_folder, "postings.txt")
vocabulary_path = os.path.join(index_folder, "vocabulary.json")


def load_vocabulary():

    with open(vocabulary_path, "r", encoding="utf-8") as file:
        vocabulary = json.load(file)

    return vocabulary


def search_word(word):

    vocabulary = load_vocabulary()

    if word not in vocabulary:
        print("Word not found in the index.")
        return

    details = vocabulary[word]

    print("\nTerm:", word)
    print("Document Frequency:", details["df"])
    print("Collection Frequency:", details["cf"])

    with open(postings_path, "rb") as file:

        file.seek(details["offset"])

        line = file.readline()

        result = json.loads(line.decode("utf-8"))

    print("\nPositional Postings:")

    for posting in result["postings"]:

        print(
            posting["document_id"],
            ":",
            posting["positions"]
        )


if __name__ == "__main__":

    print("Telugu Positional Index Search")

    word = input("\nEnter a Telugu word: ").strip()

    search_word(word)
