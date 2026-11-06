
import os
import json


project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_folder = os.path.join(project_folder, "index")
output_folder = os.path.join(project_folder, "output")

vocabulary_path = os.path.join(index_folder, "vocabulary.json")
postings_path = os.path.join(index_folder, "postings.txt")
output_path = os.path.join(output_folder, "test_results.txt")


def generate_results():

    os.makedirs(output_folder, exist_ok=True)

    with open(vocabulary_path, "r", encoding="utf-8") as file:
        vocabulary = json.load(file)

    rare_terms = []

    for term, details in vocabulary.items():

        has_telugu = any(
            "\u0C00" <= character <= "\u0C7F"
            for character in term
        )

        if details["df"] == 1 and has_telugu:
            rare_terms.append(term)

    rare_terms.sort()

    if len(rare_terms) < 10:
        print("Not enough rare terms found.")
        return

    selected_terms = rare_terms[:10]

    with open(postings_path, "rb") as postings_file:

        with open(output_path, "w", encoding="utf-8") as output_file:

            output_file.write("TELUGU POSITIONAL INDEX - TEST RESULTS\n")
            output_file.write("=" * 50 + "\n\n")

            for i in range(5):

                output_file.write("TEST CASE " + str(i + 1) + "\n")
                output_file.write("-" * 30 + "\n")

                for term in selected_terms[i * 2:i * 2 + 2]:

                    details = vocabulary[term]

                    postings_file.seek(details["offset"])

                    record = json.loads(
                        postings_file.readline().decode("utf-8")
                    )

                    postings = record["postings"]

                    actual_df = len(postings)
                    actual_cf = sum(
                        len(item["positions"])
                        for item in postings
                    )

                    output_file.write("\nTerm: " + term + "\n")
                    output_file.write("DF: " + str(details["df"]) + "\n")
                    output_file.write("CF: " + str(details["cf"]) + "\n")

                    for item in postings:
                        output_file.write(
                            item["document_id"] + ": "
                            + str(item["positions"]) + "\n"
                        )

                    if actual_df == details["df"] and actual_cf == details["cf"]:
                        output_file.write("Result: PASS\n")
                    else:
                        output_file.write("Result: FAIL\n")

                    output_file.write("\n")

            print("Test results generated successfully!")
            print("Total rare terms:", len(selected_terms))
            print("Test cases: 5")
            print("Examples: 10")
            print("Saved at:", output_path)


if __name__ == "__main__":
    generate_results()
