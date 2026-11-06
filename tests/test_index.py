
import os
import json


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_folder = os.path.join(project_folder, "index")

postings_path = os.path.join(index_folder, "postings.txt")
vocabulary_path = os.path.join(index_folder, "vocabulary.json")


def test_index():

    with open(vocabulary_path, "r", encoding="utf-8") as file:
        vocabulary = json.load(file)

    terms = ["భారతదేశం"]

    with open(postings_path, "rb") as file:

        for term in terms:

            if term not in vocabulary:
                print("Term not found:", term)
                continue

            details = vocabulary[term]

            file.seek(details["offset"])
            record = json.loads(file.readline().decode("utf-8"))

            postings = record["postings"]

            actual_df = len(postings)
            actual_cf = sum(len(item["positions"]) for item in postings)

            print("\nTerm:", term)
            print("Stored DF:", details["df"])
            print("Calculated DF:", actual_df)
            print("Stored CF:", details["cf"])
            print("Calculated CF:", actual_cf)

            if actual_df == details["df"] and actual_cf == details["cf"]:
                print("Test Passed")
            else:
                print("Test Failed")


if __name__ == "__main__":
    test_index()
